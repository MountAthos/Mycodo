#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  mycodo-client.py - Client for mycodo.py. Communicates with daemonized
#                     mycodo.py to execute commands and receive status.
#
#  Copyright (C) 2015  Kyle T. Gabriel
#
#  This file is part of Mycodo
#
#  Mycodo is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Mycodo is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Mycodo. If not, see <http://www.gnu.org/licenses/>.
#
#  Contact at kylegabriel.com

# Server status check

import rpyc
import time
import sys
import getopt
import datetime

def usage():
    print 'mycodo-client.py: Client for mycodo.py daemon (daemon must be running).\n'
    print 'Usage:  mycodo-client.py [OPTION]...\n'
    print 'Options:'
    print '    -h, --help'
    print '           Display this help and exit'
    print '        --graph theme graph_type graph_id [graph_span] [time_from] [time_to] [width]'
    print '           Generate graph, where time_from and time_to are the number of seconds since epoch'
    print '        --pidallrestart Sensor'
    print '           Restart all PIDs, where Sensor=T, HT, CO2'
    print '        --pidrestart PIDType PIDnumber'
    print '           Restart PID Controller, where PIDType=TTemp, HTTemp, HTHum, CO2, PressTemp, or PressPress'
    print '           PIDnumber=the PID controller number'
    print '        --pidstart PIDType PIDnumber'
    print '           Start PID Controller, where PIDType=TTemp, HTTemp, HTHum, CO2, PressTemp, or PressPress'
    print '           PIDnumber=the PID controller number'
    print '        --pidstop PIDType PIDnumber'
    print '           Stop PID Controller, where PIDType=TTemp, HTTemp, HTHum, CO2, PressTemp, or PressPress'
    print '           PIDnumber=the PID controller number'
    print '    -r, --relay relay state'
    print '           Turn a relay on or off. state can be 0, 1, or X.'
    print '           0=OFF, 1=ON, or X number of seconds On'
    print '        --sensort device sensor-number'
    print '           Returns a reading from the temperature and humidity sensor on GPIO pin'
    print '           Device options: DS18B20'
    print '        --sensorht device sensor-number'
    print '           Returns a reading from the temperature and humidity sensor'
    print '           Device options: DHT22, DHT11, or AM2302'
    print '        --sensorco2 device sensor-number'
    print '           Returns a reading from the CO2 sensor'
    print '           Device options: K30'
    print '        --sensorpress device sensor-number'
    print '           Returns a reading from the pressure sensor on GPIO pin'
    print '           Device options: BMP085-180'
    print '        --sqlreload relay'
    print '           Reload the SQLite database, initialize GPIO of relay if relay != -1'
    print '    -s, --status'
    print '           Return the status of the daemon and all global variables'
    print '    -t, --terminate'
    print '           Terminate the communication service and daemon'
    print '        --test-email recipient'
    print '           Send a test email'

def menu():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'hr:st',
            ["help", "graph=", "graph-custom=", "pidallrestart=", "pidrestart=", "pidstart=", "pidstop=", "relay=", "sensorco2", "sensorht", "sensorpress", "sensort", "sqlreload=", "status", "terminate", "test-email="])
    except getopt.GetoptError as err:
        print(err) # will print "option -a not recognized"
        usage()
        sys.exit(2)

    c = rpyc.connect("localhost", 18812)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return 1
        elif opt == "--graph":
            print "%s [Remote command] Graph: %s %s %s %s %s %s %s" % (
                Timestamp(), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[7])
            print "%s [Remote command] Server returned:" % (
                Timestamp()),
            if c.root.generate_graph(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[7]) == 1:
                print "Success"
            else:
                print "Fail"
            sys.exit(0)
        elif opt == "--pidallrestart":
            if (sys.argv[2] != 'T' and sys.argv[2] != 'HT' and sys.argv[2] != 'CO2' and sys.argv[2] != 'Press'):
                print "'%s' is not a valid option. Use 'T', 'HT', 'CO2', 'PressTemp', or 'PressPress'" % sys.argv[2]
                sys.exit(0)
            print "%s [Remote command] Restart all %s PID controllers: Server returned:" % (
                Timestamp(), sys.argv[2]),
            reload_status = c.root.all_pid_restart(sys.argv[2])
            if reload_status == 1:
                print "Success"
            else:
                print "Fail, %s" % reload_status
            sys.exit(1)
        elif opt == "--pidrestart":
            if (sys.argv[2] != 'TTemp' and sys.argv[2] != 'HTTemp' and sys.argv[2] != 'HTHum' and sys.argv[2] != 'CO2' and sys.argv[2] != 'PressTemp' and sys.argv[2] != 'PressPress'):
                print "'%s' is not a valid option. Use 'TTemp', 'HTTemp', 'HTHum', 'CO2', 'PressTemp', or 'PressPress'" % sys.argv[2]
                sys.exit(0)
            print "%s [Remote command] Restart %s PID controller number %s: Server returned:" % (
                Timestamp(), sys.argv[2], sys.argv[3]),
            reload_status = c.root.pid_restart(sys.argv[2], int(float(sys.argv[3])))
            if reload_status == 1:
                print "Success"
            else:
                print "Fail, %s" % reload_status
            sys.exit(1)
        elif opt == "--pidstart":
            if (sys.argv[2] != 'TTemp' and sys.argv[2] != 'HTTemp' and sys.argv[2] != 'HTHum' and sys.argv[2] != 'CO2' and sys.argv[2] != 'PressTemp' and sys.argv[2] != 'PressPress'):
                print "'%s' is not a valid option. Use 'TTemp', 'HTTemp', 'HTHum', 'CO2', 'PressTemp', or 'PressPress'" % sys.argv[2]
                sys.exit(0)
            print "%s [Remote command] Start %s PID controller number %s: Server returned:" % (
                Timestamp(), sys.argv[2], sys.argv[3]),
            reload_status = c.root.pid_start(sys.argv[2], int(float(sys.argv[3])))
            if reload_status == 1:
                print "Success"
            else:
                print "Fail, %s" % reload_status
            sys.exit(1)
        elif opt == "--pidstop":
            if (sys.argv[2] != 'TTemp' and sys.argv[2] != 'HTTemp' and sys.argv[2] != 'HTHum' and sys.argv[2] != 'CO2' and sys.argv[2] != 'PressTemp' and sys.argv[2] != 'PressPress'):
                print "'%s' is not a valid option. Use 'TTemp', 'HTTemp', 'HTHum',  'CO2', 'PressTemp', or 'PressPress'" % sys.argv[2]
                sys.exit(0)
            print "%s [Remote command] Stop %s PID controller number %s: Server returned:" % (
                Timestamp(), sys.argv[2], sys.argv[3]),
            reload_status = c.root.pid_stop(sys.argv[2], int(float(sys.argv[3])))
            if reload_status == 1:
                print "Success"
            else:
                print "Fail, %s" % reload_status
            sys.exit(1)
        elif opt in ("-r", "--relay"):
            if RepresentsInt(sys.argv[2]) and \
                int(float(sys.argv[2])) > 0:
                if (sys.argv[3] == '0' or sys.argv[3] == '1'):
                    print "%s [Remote command] Set relay %s to %s: Server returned:" % (
                        Timestamp(), int(float(sys.argv[2])), int(float(sys.argv[3]))),
                    if c.root.change_relay(int(float(sys.argv[2])),
                            int(float(sys.argv[3]))) == 1:
                        print 'success'
                    else:
                        print 'fail'
                    sys.exit(0)
                if (sys.argv[2] > 1):
                    print '%s [Remote command] Relay %s ON for %s seconds: Server returned:' % (
                        Timestamp(), int(float(sys.argv[2])), int(float(sys.argv[3]))),
                    if c.root.change_relay(int(float(sys.argv[2])),
                            int(float(sys.argv[3]))) == 1:
                        print "Success"
                    else:
                        print "Fail"
                    sys.exit(0)
            else:
                print 'Error: second input must be an integer greater than 0'
                sys.exit(1)
        elif opt == "--sensort":
            print "%s [Remote command] Read %s T sensor %s" % (
                Timestamp(), sys.argv[2], int(float(sys.argv[3])))
            temperature = c.root.read_t_sensor(sys.argv[2], int(float(sys.argv[3])))
            print "%s [Remote Command] Daemon Returned: Temperature: %s°C" % (Timestamp(), round(temperature,2))
            sys.exit(0)
        elif opt == "--sensorht":
            print "%s [Remote command] Read %s HT sensor %s" % (
                Timestamp(), sys.argv[2], int(float(sys.argv[3])))
            humidity, temperature = c.root.read_ht_sensor(sys.argv[2], int(float(sys.argv[3])))
            print "%s [Remote Command] Daemon Returned: Temperature: %s°C Humidity: %s%%" % (Timestamp(), round(temperature,2), round(humidity,2))
            sys.exit(0)
        elif opt == "--sensorco2":
            print "%s [Remote command] Read %s CO2 sensor %s" % (
                Timestamp(), sys.argv[2], int(float(sys.argv[3])))
            co2 = c.root.read_co2_sensor(sys.argv[2], int(float(sys.argv[3])))
            print "%s [Remote Command] Daemon Returned: CO2: %s ppmv" % (Timestamp(), co2)
            sys.exit(0)
        elif opt == "--sensorpress":
            print "%s [Remote command] Read %s Press sensor %s" % (
                Timestamp(), sys.argv[2], int(float(sys.argv[3])))
            pressure, temperature, altitude = c.root.read_press_sensor(sys.argv[2], int(float(sys.argv[3])))
            print "%s [Remote Command] Daemon Returned: Pressure: %s kPa Temperature: %s°C Altitude: %s m" % (Timestamp(), pressure, round(temperature,2), round(altitude,2))
            sys.exit(0)
        
        elif opt == "--sqlreload":
            if int(float(sys.argv[2])) != -1:
                print "%s [Remote command] Reload SQLite database and initialize relay %s: Server returned:" % (
                    Timestamp(), int(float(sys.argv[2]))),
                if c.root.sqlreload(int(float(sys.argv[2]))) == 1:
                    print "Success"
                else:
                    print "Fail"
            else:
                print "%s [Remote command] Reload SQLite database: Server returned:" % (
                    Timestamp()),
                if c.root.sqlreload(-1) == 1:
                    print "Success"
                else:
                    print "Fail"
            sys.exit(0)
        elif opt in ("-s", "--status"):
            print "%s [Remote command] Request Status Report: Daemon is active:" % (
                Timestamp()),
            output, names, values = c.root.status(1)
            if output == 1:
                print "Yes"
                print "Parsing global variables..."
            else:
                print "No"

            padding = 36
            for nam, val in zip(names, values):
                print "%s %s" % (nam.ljust(padding), val)

            sys.exit(0)
        elif opt in ("-t", "--terminate"):
            print "%s [Remote command] Terminate all threads and daemon: Server returned:" % (
                Timestamp()),
            if c.root.terminate_daemon(1) == 1: print "Success"
            else: print "Fail"
            sys.exit(0)
        elif opt == "--test-email":
            print "%s [Remote command] Send test email to %s: Server returned:" % (
                Timestamp(), sys.argv[2]),
            if c.root.test_email(sys.argv[2]) == 1:
                print "Success (check your email for confirmation)"
            else:
                print "Fail"
            sys.exit(1)
        else:
            assert False, "Fail"
    usage()
    sys.exit(1)

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def Timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y %m %d %H %M %S')

if len(sys.argv) == 1: # No arguments given
    usage()
    sys.exit(1)

menu()
sys.exit(0)
