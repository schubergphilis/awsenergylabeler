from awsenergylabelerlib import (EnergyLabeler,
                                 AwsAccount,
                                 SecurityHub,
                                 ACCOUNT_THRESHOLDS,
                                 LANDING_ZONE_THRESHOLDS,
                                 DEFAULT_SECURITY_HUB_FILTER,
                                 DEFAULT_SECURITY_HUB_FRAMEWORKS,
                                 ALL_LANDING_ZONE_EXPORT_TYPES,
                                 LANDING_ZONE_METRIC_EXPORT_TYPES,
                                 ALL_ACCOUNT_EXPORT_TYPES,
                                 ACCOUNT_METRIC_EXPORT_TYPES)


#  pylint: disable=too-many-arguments
def get_landing_zone_reporting_data(landing_zone_name,
                                    region,
                                    allowed_account_ids,
                                    denied_account_ids,
                                    allowed_regions,
                                    denied_regions,
                                    export_all_data_flag):
    """Gets the reporting data for a landing zone.

    Args:
        landing_zone_name: The name of the landing zone.
        region: The home region of AWS.
        allowed_account_ids: The allowed account ids for landing zone inclusion if any.
        denied_account_ids: The allowed account ids for landing zone exclusion if any.
        allowed_regions: The allowed regions for security hub if any.
        denied_regions: The denied regions for security hub if any.
        export_all_data_flag: If set all data is going to be exported, else only basic reporting.

    Returns:
        report_data, exporter_arguments

    """
    labeler = EnergyLabeler(landing_zone_name=landing_zone_name,
                            region=region,
                            account_thresholds=ACCOUNT_THRESHOLDS,
                            landing_zone_thresholds=LANDING_ZONE_THRESHOLDS,
                            security_hub_filter=DEFAULT_SECURITY_HUB_FILTER,
                            frameworks=DEFAULT_SECURITY_HUB_FRAMEWORKS,
                            allowed_account_ids=allowed_account_ids,
                            denied_account_ids=denied_account_ids,
                            allowed_regions=allowed_regions,
                            denied_regions=denied_regions)
    report_data = [['Landing Zone:', labeler.landing_zone.name],
                   ['Landing Zone Security Score:', labeler.landing_zone_energy_label.label],
                   ['Landing Zone Percentage Coverage:', labeler.landing_zone_energy_label.coverage],
                   ['Labeled Accounts Measured:', labeler.labeled_accounts_energy_label.accounts_measured]]
    if labeler.landing_zone_energy_label.best_label != labeler.landing_zone_energy_label.worst_label:
        report_data.extend([['Best Account Security Score:', labeler.landing_zone_energy_label.best_label],
                            ['Worst Account Security Score:', labeler.landing_zone_energy_label.worst_label]])
    export_types = ALL_LANDING_ZONE_EXPORT_TYPES if export_all_data_flag else LANDING_ZONE_METRIC_EXPORT_TYPES
    exporter_arguments = {'export_types': export_types,
                          'name': labeler.landing_zone.name,
                          'energy_label': labeler.landing_zone_energy_label.label,
                          'security_hub_findings': labeler.security_hub_findings,
                          'labeled_accounts': labeler.landing_zone_labeled_accounts}
    return report_data, exporter_arguments


#  pylint: disable=too-many-arguments
def get_account_reporting_data(account_id,
                               region,
                               allowed_regions,
                               denied_regions,
                               export_all_data_flag):
    """Gets the reporting data for a single account.

    Args:
        account_id: The ID of the account to get reporting on.
        region: The home region of AWS.
        allowed_regions: The allowed regions for security hub if any.
        denied_regions: The denied regions for security hub if any.
        export_all_data_flag: If set all data is going to be exported, else only basic reporting.

    Returns:
        report_data, exporter_arguments

    """
    account = AwsAccount(account_id, 'Not Retrieved', ACCOUNT_THRESHOLDS)
    security_hub = SecurityHub(region=region,
                               allowed_regions=allowed_regions,
                               denied_regions=denied_regions)
    query_filter = SecurityHub.calculate_query_filter(DEFAULT_SECURITY_HUB_FILTER,
                                                      allowed_account_ids=[account_id],
                                                      denied_account_ids=None,
                                                      frameworks=DEFAULT_SECURITY_HUB_FRAMEWORKS)
    security_hub_findings = security_hub.get_findings(query_filter)
    account.calculate_energy_label(security_hub_findings)
    report_data = [['Account ID:', account.id],
                   ['Account Security Score:', account.energy_label.label],
                   ['Number Of Critical & High Findings:', account.energy_label.number_of_critical_high_findings],
                   ['Number Of Medium Findings:', account.energy_label.number_of_medium_findings],
                   ['Number Of Low Findings:', account.energy_label.number_of_low_findings],
                   ['Max Days Open:', account.energy_label.max_days_open]]
    if account.alias:
        report_data.append(['Account Alias:', account.alias])
    export_types = ALL_ACCOUNT_EXPORT_TYPES if export_all_data_flag else ACCOUNT_METRIC_EXPORT_TYPES
    exporter_arguments = {'export_types': export_types,
                          'name': account.id,
                          'energy_label': account.energy_label.label,
                          'security_hub_findings': security_hub_findings,
                          'labeled_accounts': account}
    return report_data, exporter_arguments
