import logging
from awsenergylabelerlib import (DestinationPath,
                                 DataExporter)
from chalice import Chalice, Rate
from datetime import datetime

from chalicelib.exceptions import (InvalidDestinationPath)
from chalicelib.retrievers import (get_landing_zone_reporting_data,
                                   get_account_reporting_data)
from chalicelib.validators import (get_mutually_exclusive,
                                   get_required_variable,
                                   get_environment_boolean,
                                   get_log_level)


def main(logger):
    """Main method."""
    landing_zone_name, single_account_id = get_mutually_exclusive('LANDING_ZONE_NAME', 'SINGLE_ACCOUNT_ID')
    region = get_required_variable('REGION')
    allowed_account_ids, denied_account_ids = get_mutually_exclusive('ALLOWED_ACCOUNT_IDS', 'DENIED_ACCOUNT_IDS')
    allowed_regions, denied_regions = get_mutually_exclusive('ALLOWED_REGIONS', 'DENIED_REGIONS')
    export_all_data_flag = get_environment_boolean('EXPORT_ALL_DATA', default_value=False)
    log_level = get_log_level('LOG_LEVEL')
    export_path = get_required_variable('EXPORT_PATH')
    if DestinationPath(export_path).type != 's3':
        raise InvalidDestinationPath(export_path)
    date_export_path = f"{export_path}{datetime.now().year}/{datetime.now().month}/{datetime.now().day}/"
    logger.setLevel(getattr(logging, log_level))
    logger.getLogger('botocore').setLevel(logging.ERROR)
    try:
        if landing_zone_name:
            report_data, exporter_arguments = get_landing_zone_reporting_data(landing_zone_name=landing_zone_name,
                                                                              region=region,
                                                                              allowed_account_ids=allowed_account_ids,
                                                                              denied_account_ids=denied_account_ids,
                                                                              allowed_regions=allowed_regions,
                                                                              denied_regions=denied_regions,
                                                                              export_all_data_flag=export_all_data_flag)
        else:
            report_data, exporter_arguments = get_account_reporting_data(account_id=single_account_id,
                                                                         region=region,
                                                                         allowed_regions=allowed_regions,
                                                                         denied_regions=denied_regions,
                                                                         export_all_data_flag=export_all_data_flag)
        logger.info(f'Trying to export data to the requested path : {date_export_path}')
        exporter = DataExporter(**exporter_arguments)
        exporter.export(date_export_path)
    except Exception as msg:
        logger.error(msg)
        return False
    return True


app = Chalice(app_name="EnergyLabeler")


@app.schedule(Rate(7, unit=Rate.DAYS))
def handler(event):
    main(app.log)
