       IDENTIFICATION DIVISION.
       PROGRAM-ID. PAYROLL-CALCULATOR.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  EMPLOYEE-DATA.
           05 EMPLOYEE-ID           PIC 9(5).
           05 EMPLOYEE-NAME         PIC X(30).
           05 HOURS-WORKED          PIC 9(3)V9.
           05 HOURLY-RATE           PIC 9(3)V99.
           05 GROSS-PAY             PIC 9(6)V99.
           05 TAX-AMOUNT            PIC 9(6)V99.
           05 NET-PAY               PIC 9(6)V99.
       
       01  TAX-RATE                 PIC 9V99 VALUE 0.20.
       
       PROCEDURE DIVISION.
       MAIN-LOGIC.
           PERFORM INITIALIZE-DATA
           PERFORM CALCULATE-GROSS-PAY
           PERFORM CALCULATE-TAXES
           PERFORM CALCULATE-NET-PAY
           PERFORM DISPLAY-PAYROLL
           STOP RUN.
       
       INITIALIZE-DATA.
           MOVE 12345 TO EMPLOYEE-ID
           MOVE "JOHN SMITH" TO EMPLOYEE-NAME
           MOVE 40.0 TO HOURS-WORKED
           MOVE 25.50 TO HOURLY-RATE.
       
       CALCULATE-GROSS-PAY.
           COMPUTE GROSS-PAY = HOURS-WORKED * HOURLY-RATE
           DISPLAY "Calculating gross pay for " EMPLOYEE-NAME.
       
       CALCULATE-TAXES.
           COMPUTE TAX-AMOUNT = GROSS-PAY * TAX-RATE
           DISPLAY "Tax rate: " TAX-RATE.
       
       CALCULATE-NET-PAY.
           COMPUTE NET-PAY = GROSS-PAY - TAX-AMOUNT.
       
       DISPLAY-PAYROLL.
           DISPLAY " "
           DISPLAY "===== PAYROLL STATEMENT ====="
           DISPLAY "Employee ID: " EMPLOYEE-ID
           DISPLAY "Name: " EMPLOYEE-NAME
           DISPLAY "Hours: " HOURS-WORKED
           DISPLAY "Rate: $" HOURLY-RATE
           DISPLAY "Gross Pay: $" GROSS-PAY
           DISPLAY "Tax: $" TAX-AMOUNT
           DISPLAY "Net Pay: $" NET-PAY.

