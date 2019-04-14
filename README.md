
![Imgur](https://imgur.com/ifvxgtR)<br><br>
In colaboration with [BBrunoEsteves](https://github.com/BBrunoEsteves).



<br><br> <br><br>
### Theory
[EOG wiki](https://en.wikipedia.org/wiki/Electrooculography)<br><br>
![Imgur](https://i.imgur.com/HOOcWlC.png)

<br><br><br><br>
### Signal aquisition hardware
The following circuit was responsible for amplifying and filtering the signal from the electrodes.<br><br>
The circuit was implemented twice, for the Horizontal and Vertical channels respectively.<br><br>
![Imgur](https://i.imgur.com/GUXpgGK.png)

<br><br><br><br>
### Data sampling and comunication
A Microcontroler Atmega324 was used for sampling and sending the signal to the PC(Through serial comunication), in order to develop knowledge about low level programming with assembly. A simpler alternative would be to use an Arduino.<br><br>
Each data package was encoded in one Byte, containing the sampled value(7 MSBs) and corresponding channel(0-Vertical, 1-Horizontal).<br><br>
![Imgur](https://i.imgur.com/sy3vHCL.png)

<br><br><br><br>
### Data processing and display
A Python script was used to comunicate(PySerial), process and display(PyQtGraph) the signals. The script is capable of receiving and displaying data at speeds above 1KHz.<br><br>
Aditionaly, the signal can be used to detect the direction that the user is looking, through simple thresholding, enabling the control of the SnakeGame.<br><br>
![Imgur](https://i.imgur.com/WtQyL0G.png)

<br><br><br><br>
### Snake game
A simple game of Snake implemented with pygame.<br><br>
![Imgur](https://i.imgur.com/e9gpq7c.png])
