# Integrated Circuits - Popular Datasheets Reference Guide

## Overview

This document provides references to commonly used integrated circuits and their technical specifications. PDFs can be downloaded from the manufacturer links provided.

## Timer ICs

### NE555 - Precision Timer
**Manufacturer:** Texas Instruments  
**Function:** General-purpose timer  
**Package:** DIP-8, SOIC-8, TSSOP-8  
**Supply Voltage:** 4.5V to 16V  
**Key Features:**
- Timing from microseconds to hours
- Astable or monostable operation
- Adjustable duty cycle
- TTL-compatible output (can sink/source up to 200mA)
- Quiescent current: 2mA typical

**Datasheet Link:** https://www.ti.com/lit/gpn/ne555

**Pin Configuration:**
```
GND   (1) -|o  |- (8) VCC
TRIG  (2) ---  --- (7) DISCH
OUT   (3) --- 555 --- (6) THRES
RESET (4) ---  --- (5) CONT
```

**Applications:**
- Astable multivibrator (oscillator)
- Monostable multivibrator (one-shot)
- Frequency dividers
- LED flashers
- Audio oscillators

---

## Operational Amplifiers

### LM741 - General Purpose Op-Amp
**Manufacturer:** Texas Instruments / National Semiconductor  
**Supply Voltage:** ±5V to ±18V (single supply compatible)  
**Gain Bandwidth Product:** 1 MHz  
**Slew Rate:** 0.5V/μs  
**Input Impedance:** 2MΩ typical

**Key Features:**
- Short circuit protection
- Offset voltage adjustment
- Compensation capacitor
- Low power consumption

**Common Applications:**
- Inverting amplifiers
- Non-inverting amplifiers
- Comparators
- Summing amplifiers
- Integrators and differentiators

---

## Logic ICs

### 7400 Series TTL Logic Gates

#### 7400 - Quad NAND Gate
**Package:** DIP-14  
**Supply Voltage:** 5V  
**Propagation Delay:** 10ns typical  
**Logic Family:** TTL (Transistor-Transistor Logic)

**Pin Configuration:**
- 1A, 1B inputs, 1Y output
- 2A, 2B inputs, 2Y output  
- 3A, 3B inputs, 3Y output
- 4A, 4B inputs, 4Y output

#### 7402 - Quad NOR Gate
**Package:** DIP-14  
**Supply Voltage:** 5V

#### 7404 - Hex Inverter
**Package:** DIP-14  
**Supply Voltage:** 5V

#### 7486 - Quad XOR Gate
**Package:** DIP-14  
**Supply Voltage:** 5V

---

### 4000 Series CMOS Logic Gates

#### 4011 - Quad NAND Gate
**Manufacturer:** Various (Fairchild, TI, etc.)  
**Supply Voltage:** 3V to 15V  
**Power Consumption:** Much lower than TTL  
**Logic Family:** CMOS

**Advantages over TTL:**
- Lower power consumption
- Wider supply voltage range
- Better noise immunity at logic threshold
- Higher input impedance

---

## Microcontrollers

### ATmega328P - 8-bit AVR Microcontroller
**Manufacturer:** Microchip  
**Architecture:** 8-bit RISC  
**Flash Memory:** 32KB  
**SRAM:** 2KB  
**Clock Speed:** 16MHz maximum  
**Package:** DIP-28, TQFP-32

**Key Features:**
- 23 general purpose I/O pins
- SPI, I2C, UART interfaces
- 6 ADC channels
- 6 PWM channels
- Timer/Counters

**Popular in:**
- Arduino Uno boards
- Embedded systems
- IoT devices

---

### PIC16F877A - 8-bit PIC Microcontroller
**Manufacturer:** Microchip  
**Flash Memory:** 14KB  
**SRAM:** 368 bytes  
**EEPROM:** 256 bytes  
**Clock Speed:** 20MHz maximum
**Package:** DIP-40, TQFP-44

**Key Features:**
- 40 I/O pins
- 8 ADC channels
- UART, SPI, I2C support
- Watchdog timer
- Sleep mode

---

## Voltage Regulators

### LM7805 - 5V Positive Regulator
**Output Voltage:** 5V  
**Output Current:** 1.5A typical  
**Input Voltage Range:** 7V to 20V  
**Dropout Voltage:** ~2V

**Applications:**
- Regulated power supply for digital circuits
- Microcontroller power supply

**Pin Configuration:**
```
IN (1) --- |o  |- (3) OUT
GND (2) --- --- 
```

### LM7812 - 12V Positive Regulator
**Output Voltage:** 12V  
**Output Current:** 1.5A typical  
**Input Voltage Range:** 14.5V to 30V

### LM7905 - 5V Negative Regulator
**Output Voltage:** -5V  
**Output Current:** 1.5A typical  
**Input Voltage Range:** -7V to -20V

---

## Power Management ICs

### LM1117 - Low Dropout (LDO) Regulator
**Output Voltage:** 1.8V, 2.5V, 3.3V, 5V  
**Output Current:** 800mA  
**Dropout Voltage:** 1.2V @ 800mA  
**Package:** SOT-223, DIP-8

**Advantages:**
- Lower dropout voltage than 78XX series
- Lower quiescent current
- Smaller package options

---

## Audio ICs

### LM386 - Low Voltage Audio Amplifier
**Supply Voltage:** 4V to 12V  
**Output Power:** 1W @ 8Ω (5V supply)  
**Gain:** 20V/V to 200V/V (adjustable)  
**Bandwidth:** 100kHz

**Applications:**
- Portable audio amplification
- Speaker drivers
- Intercom systems

---

## Common IC Package Types

### DIP (Dual In-Line Package)
- Through-hole mounted
- Easy to use on breadboards
- Larger than SMD alternatives

### SOIC (Small-Outline Integrated Circuit)
- Surface-mount
- 1.27mm pitch
- Smaller than DIP
- Soldering required

### TQFP (Thin Quad Flat Pack)
- Surface-mount
- Square package
- 0.5mm pin pitch
- Used for high pin-count ICs

### BGA (Ball Grid Array)
- Surface-mount
- Solder balls on underside
- Requires specialized equipment
- Most compact option

---

## Datasheet Resources

### Manufacturer Links
- **Texas Instruments:** www.ti.com (search product page for PDF)
- **Microchip (Atmel):** www.microchip.com
- **STMicroelectronics:** www.st.com
- **NXP Semiconductors:** www.nxp.com
- **Infineon:** www.infineon.com

### Third-Party Datasheet Sites
- **AllDataSheet:** www.alldatasheet.com
- **DatasheetsPDF:** www.datasheetspdf.com
- **IC Master:** www.icmaster.com

### How to Download PDFs
1. Visit manufacturer product page
2. Look for "Documentation" or "Technical Documents" section
3. Select PDF format
4. Download directly to your computer

---

## Reading Datasheets - Key Sections

### Electrical Characteristics
- Absolute maximum ratings (do not exceed!)
- Operating conditions
- DC characteristics
- AC characteristics
- Timing specifications

### Pin Configuration
- Pin names and numbers
- Pin descriptions
- Signal types (input, output, power, ground)

### Applications
- Typical circuit diagrams
- Application notes
- Design considerations

### Package Information
- Physical dimensions
- Pin spacing
- Thermal characteristics
- Soldering recommendations

---

## Best Practices

1. **Always check absolute maximum ratings** before design
2. **Use recommended operating conditions** for reliable operation
3. **Review application circuits** in the datasheet
4. **Pay attention to timing specifications** for digital circuits
5. **Check thermal management** requirements for power ICs
6. **Review PCB layout recommendations** from manufacturer
7. **Use decoupling capacitors** as specified

---

## Notes

This document serves as a quick reference guide. For detailed specifications, always consult the official datasheet from the IC manufacturer.

Last updated: November 11, 2025
