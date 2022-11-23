from chalice import Chalice, Rate

import datetime
import json
import logging

from art import text2art
from terminaltables import AsciiTable
from awsenergylabelerlib import DataExporter, DEFAULT_SECURITY_HUB_FRAMEWORKS
from awsenergylabelerlib._version import __version__ as lib_version
from awsenergylabelercli._version import __version__ as cli_version

from awsenergylabelercli import (calculate_file_hash,
                                 get_account_reporting_data,
                                 get_arguments,
                                 get_zone_reporting_data,
                                 setup_logging)
from awsenergylabelercli.entities import MetadataEntry, Metadata


def create_execution_metadata(args):
    """Creates the execution metadata.

    Args:
        args: The arguments provided by argparse as set by the user.

    Returns:
        The calculated metadata.

    """
    metadata = Metadata()
    metadata.add_entry(MetadataEntry(title='Default Account Thresholds Overwritten:',
                                     value=bool(args.account_thresholds),
                                     is_report_entry=True))
    if args.account_thresholds:
        metadata.add_entry(MetadataEntry(title='Account Thresholds Provided:',
                                         value=args.account_thresholds,
                                         is_report_entry=False))
    metadata.add_entry(MetadataEntry(title='Default Zone Thresholds Overwritten:',
                                     value=bool(args.zone_thresholds),
                                     is_report_entry=True))
    if args.zone_thresholds:
        metadata.add_entry(MetadataEntry(title='Zone Thresholds Provided:',
                                         value=args.zone_thresholds,
                                         is_report_entry=False))
    metadata.add_entry(MetadataEntry(title='Default Security Hub Query Filter Overwritten:',
                                     value=bool(args.security_hub_query_filter),
                                     is_report_entry=True))
    if args.security_hub_query_filter:
        metadata.add_entry(MetadataEntry(title='Security Hub Query Filter Provided:',
                                         value=args.security_hub_query_filter,
                                         is_report_entry=False))

    if set(args.frameworks) != set(DEFAULT_SECURITY_HUB_FRAMEWORKS):
        metadata.add_entry(MetadataEntry(title='Default Frameworks Overwritten:',
                                         value=True,
                                         is_report_entry=True))
        metadata.add_entry(MetadataEntry(title='Frameworks Provided:',
                                         value=args.frameworks,
                                         is_report_entry=False))
    metadata.add_entry(MetadataEntry(title='Library Version:',
                                     value=lib_version,
                                     is_report_entry=True))
    metadata.add_entry(MetadataEntry(title='Cli Version:',
                                     value=cli_version,
                                     is_report_entry=True))
    return metadata


def _get_reporting_arguments(args):
    start_run_time = datetime.datetime.now()
    execution_metadata = create_execution_metadata(args)
    method_arguments = {'region': args.region,
                        'frameworks': args.frameworks,
                        'allowed_regions': args.allowed_regions,
                        'denied_regions': args.denied_regions,
                        'report_closed_findings_days': args.report_closed_findings_days,
                        'report_suppressed_findings': args.report_suppressed_findings,
                        'account_thresholds': args.account_thresholds,
                        'export_all_data_flag': args.export_all,
                        'security_hub_query_filter': args.security_hub_query_filter,
                        'log_level': args.log_level,
                        'metadata': execution_metadata}
    if args.single_account_id:
        get_reporting_data = get_account_reporting_data
        method_arguments.update({'account_id': args.single_account_id})
    else:
        zone_type = 'organizations_zone' if args.organizations_zone_name else 'audit_zone'
        zone_name = args.organizations_zone_name or args.audit_zone_name
        get_reporting_data = get_zone_reporting_data
        method_arguments.update({'zone_name': zone_name,
                                 'allowed_account_ids': args.allowed_account_ids,
                                 'denied_account_ids': args.denied_account_ids,
                                 'zone_type': zone_type,
                                 'zone_thresholds': args.zone_thresholds})
    report_data, exporter_arguments = get_reporting_data(**method_arguments)
    execution_metadata = exporter_arguments.get('metadata')
    report_data.extend(execution_metadata.report_table)
    end_run_time = datetime.datetime.now()
    execution_metadata.add_entry(MetadataEntry(title='Date and time of end of execution:',
                                               value=str(end_run_time),
                                               is_report_entry=True))
    execution_metadata.add_entry(MetadataEntry(title='Duration of run:',
                                               value=str(end_run_time - start_run_time),
                                               is_report_entry=True))
    execution_metadata.add_entry(MetadataEntry(title='Hash:',
                                               value=calculate_file_hash(
                                                   json.dumps(execution_metadata.data).encode('utf-8')),
                                               is_report_entry=False))
    exporter_arguments.update({'metadata': execution_metadata.data})
    return report_data, exporter_arguments


def report(report_data, to_json=False):
    """Report to table or json."""
    if to_json:
        data = {key.replace(':', '').replace(' ', '_').lower(): value for key, value in dict(report_data).items()}
        print(json.dumps(data, indent=2))
        return None
    table_data = [['Energy label report']]
    table_data.extend(report_data)
    table = AsciiTable(table_data)
    print(table.table)
    return None


def main(logger):
    """Main method."""
    args = get_arguments()
    logging.getLogger('botocore').setLevel(logging.ERROR)
    for entity in ['account', 'zone']:
        if getattr(args, f'{entity}_thresholds'):
            logger.warning(f'{entity.capitalize()} thresholds have been overwritten, '
                           f'configuration will be reported on the output.')
    if not args.frameworks:
        logger.info('No frameworks have been provided for filtering.')
    try:
        print(text2art("AWS Energy Labeler"))
        report_data, exporter_arguments = _get_reporting_arguments(args)
        if args.export_path:
            logger.info(f'Trying to export data to the requested path : {args.export_path}')
            exporter = DataExporter(**exporter_arguments)
            exporter.export(args.export_path)
        report(report_data, args.to_json)
        status_code = 0
    except Exception as msg:  # pylint: disable=broad-except
        logger.error(msg)
        status_code = 1
    return status_code


app = Chalice(app_name="EnergyLabeler")


@app.schedule(Rate(7, unit=Rate.DAYS))
def handler(event):
    main(app.log)
