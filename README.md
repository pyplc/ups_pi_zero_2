# **Intelligent ups for Raspberry pi zero w2**

Here an unable power supply for Raspberry Zero W2 is realized with the help of Raspberry Pico.
The Raspberry Pico takes over the logic for the power supply here, in the event of a power failure the Pico communicates via the serial port to the Zero w2 and reports a power failure, the Zero w2 can then shut down after a defined time. If the voltage is ok again, the Zero w2 starts automatically. A Li-ion battery with an integrated protection circuit is used for the technical implementation.
Micropython Script is used as a program on the Raspberry Pico side and Python on the Raspberry Zero w2.

Schema v0.1
![](https://github.com/pyplc/ups_pi_zero_2/blob/main/doc/Schema_v0_1.png)

PCB v0.1
![](https://github.com/pyplc/ups_pi_zero_2/blob/main/doc/ups_pyplc_v0.1.png)

Hardware v0.1
![](https://github.com/pyplc/ups_pi_zero_2/blob/main/doc/hardware_v0_1.png)


Din rail case - APRA HO6

![](https://github.com/pyplc/ups_pi_zero_2/blob/main/doc/DIN_Enclose_Apra.png)
