

import wellcounter_optimisation_module as wom

# Get the current date
current_date = date.today().strftime("%Y%m%d")

# Set up logging
logging.basicConfig(filename=f'optimize_imaging_parameters_{current_date}_logfile.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

wom.batch_optimizer(config_path="wellcounter_config.yml")