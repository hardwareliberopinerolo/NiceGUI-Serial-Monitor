import serial
import serial.tools.list_ports

import asyncio
from nicegui import app, run, ui

port = serial.Serial()
port.baudrate = 115200 #default value
port.port = "/dev/ttyACM0" #default value - For Window change with "COM3"

def openSerialPort() -> None:
	#port.port = "/dev/ttyACM0" #"COM30"
	#port.baudrate = 115200
	port.bytesize = serial.EIGHTBITS #number of bits per bytes
	port.parity = serial.PARITY_NONE #set parity check: no parity
	port.stopbits = serial.STOPBITS_ONE #number of stop bits
	port.timeout = 1            #non-block read
	port.xonxoff = False     #disable software flow control
	port.rtscts = False     #disable hardware (RTS/CTS) flow control
	port.dsrdtr = False       #disable hardware (DSR/DTR) flow control

	try:
		log.push(port.baudrate) 
		port.open()
	except:
		ui.notify("serial port not open")
		log.push("serial port not open")
	else:
		log.push("serial port open")
		ui.notify("serial port open")

def closeSerialPort() -> None:
	port.close()


#Send command to Serial
ui.input('Send command').on('keydown.enter', lambda e: (
	port.write(f'{e.sender.value}\n'.encode()),
	e.sender.set_value(''), ))

log = ui.log()

def clean_monitor() -> None:
	log.clear()

#Read data from Serial
async def read_loop() -> None:
	while not app.is_stopped:
		if port.is_open:
			try:
				line = await run.io_bound(port.readline)
				if line:
					log.push(line.decode())
			except:
				log.push("serial baudrate wrong")
				ui.notify("serial baudrate wrong")
			#else:
			#	log.push("serial baudrate ok")
			#	ui.notify("serial baudrate ok")
		else:
			await asyncio.sleep(0.2)

app.on_startup(read_loop)

with ui.row():
	select1 = ui.select(["/dev/ttyACM0", "/dev/ttyACM1","/dev/ttyUSB0","/dev/ttyUSB1" ], value="/dev/ttyACM0", on_change = lambda e: (log.push(e.value) ,setattr(port, 'port', e.value)))
	select2 = ui.select([9600, 115200], value=9600, on_change = lambda e: (log.push(e.value) ,setattr(port, 'baudrate', e.value)))

select1.value = port.port
select2.value = port.baudrate


for ports in serial.tools.list_ports.comports():
	log.push(f'Current port: {ports}')



with ui.row():
	ui.button('Open Serial Port', on_click=openSerialPort)
	ui.button('Close Serial Port', on_click=closeSerialPort)
	ui.button('Clean Monitor', on_click=clean_monitor)
ui.run()
