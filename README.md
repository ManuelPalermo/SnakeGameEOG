
![Imgur](https://i.imgur.com/BVBFMpf.png)


<br><br> <br><br> <br><br>
### Theory
[EOG wiki](https://en.wikipedia.org/wiki/Electrooculography)
![Imgur](https://i.imgur.com/HOOcWlC.png)

### Signal aquisition hardware
The following circuit was responsible for amplifying and filtering the signal from the electrodes.
The circuit was implemented twice, for the Horizontal and Vertical channels respectively.
![Imgur](https://i.imgur.com/GUXpgGK.png)

### Data sampling and comunication
A Microcontroler Atmega324 was used for sampling and sending the signal to the PC(Through serial comunication), in order to develop knowledge about low level programming with assembly. A simpler alternative would be to use an Arduino.
Each data package was encoded in one Byte, containing the sampled value(7 MSBs) and corresponding channel(0-Vertical, 1-Horizontal).
![Imgur](https://i.imgur.com/sy3vHCL.png)

### Data processing and display
A Python script was used to comunicate(PySerial), process and display(PyQtGraph) the signals. The script is capable of receiving and displaying data at speeds above 1KHz.
Aditionaly, the signal can be used to detect the direction that the user is looking, through simple thresholding, enabling the control of the SnakeGame.
![Imgur](https://i.imgur.com/WtQyL0G.png)

### Snake game
A simple game of Snake implemented with pygame.
![Imgur](https://i.imgur.com/e9gpq7c.png])
