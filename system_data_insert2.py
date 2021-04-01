import psutil
from influxdb import InfluxDBClient
import time
import pdb
import requests
import json

#client = InfluxDBClient(host='localhost', port=8086)
#client.create_database('system')

INFLUX_URL='localhost'
ORG='BABBITT'
BUCKET_NAME='tab'

QUERY_URI='http://{}:8086/api/v2/write?org={}&bucket={}&precision=ms'.format(INFLUX_URL,ORG,BUCKET_NAME)
INFLUX_TOKEN='FtDzXCyHxW9PYg_rbVIF-5vuekBSUgj_BGWoM3GwP3YU1fjfdc7N1RFT_9CirtvS43PVPeI9fouOyciA2UEuwA=='
headers = {}
headers['Authorization'] = 'Token {}'.format(INFLUX_TOKEN)
#client = InfluxDBClient(host=INFLUXDB_HOST, port=8086)


measurement_name = 'system_data'
data_end_time = int(time.time() * 1000)
data = []
cpu_p, mem_p, disk_read, disk_write, net_sent_now, net_recv_now, temp, \
    boot_time, net_sent_prev, net_recv_prev = \
    0, 0, 0, 0, 0, 0, 0, 0, \
    psutil.net_io_counters().bytes_sent, psutil.net_io_counters().bytes_recv


def get_system_data(num):
    global cpu_p, mem_p, disk_write, disk_read, net_recv_now, net_sent_now,\
        temp, boot_time, data_end_time
    data_end_time = int(time.time() * 1000)
    cpu_p = psutil.cpu_percent()
    mem_p = psutil.virtual_memory().percent
    #disk_read = psutil.disk_io_counters().read_count
    #disk_read = 0
    #disk_write = psutil.disk_io_counters().write_count
    net_sent_now = psutil.net_io_counters().bytes_sent
    net_recv_now = psutil.net_io_counters().bytes_recv
    #temp = psutil.sensors_temperatures()['acpitz'][0].current
    boot_time = psutil.boot_time()

    """
    data.append(
        {
            "measurement": "system_data",
            "tags": {
                "boot_time": boot_time
            },
            "fields": {
                "cpu_percent": cpu_p,
                "memory_percent": mem_p,
                "net_sent": net_sent_now-net_sent_prev,
                "net_received": net_recv_now-net_recv_prev,
     #           "temperature": temp,
            },
            "time": data_end_time
        }
    )
    """
    
    data.append("system_data,boot_time={} cpu_percent={},memory_percent={},net_sent={},net_received={} {}".format(boot_time,cpu_p,mem_p,net_sent_now-net_sent_prev,net_recv_now-net_recv_prev,data_end_time))
    
    #client.write_points(data, database='system', time_precision='ms',
    #                    protocol='json')
    r = requests.post(QUERY_URI, data=data[num], headers=headers)
    print( r.status_code, data[num])

def run(interval=1):  # interval in seconds
    global net_recv_prev, net_sent_prev
    print("Script is running, press Ctrl+C to stop!")
    x=0
    while 1:
        try:
            get_system_data(x)
            net_sent_prev = psutil.net_io_counters().bytes_sent
            net_recv_prev = psutil.net_io_counters().bytes_recv
            x+=1
            time.sleep(interval)
        except KeyboardInterrupt:
            quit()
        except Exception as e:
            print("Uh oh something went wrong", e)


run()
