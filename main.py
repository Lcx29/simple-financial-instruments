import config.logging_config as logging_config
import institutions.bochk.exchange_rate as bochk_exchange_rate

def boc_hk_exchange_rate():
    bochk_exchange_rate.request_data_from_network()


if __name__ == "__main__":
    logging_config.init_yml_log()
    boc_hk_exchange_rate()
