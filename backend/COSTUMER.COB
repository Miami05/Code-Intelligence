       IDENTIFICATION DIVISION.
       PROGRAM-ID. CUSTOMER-MANAGER.
       AUTHOR. CODE-INTELLIGENCE-SYSTEM.
       
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT CUSTOMER-FILE ASSIGN TO "CUSTOMERS.DAT"
               ORGANIZATION IS INDEXED
               ACCESS MODE IS DYNAMIC
               RECORD KEY IS CUSTOMER-ID.
       
       DATA DIVISION.
       FILE SECTION.
       FD  CUSTOMER-FILE.
       01  CUSTOMER-RECORD.
           05 CUSTOMER-ID           PIC 9(6).
           05 CUSTOMER-NAME         PIC X(50).
           05 CUSTOMER-EMAIL        PIC X(50).
           05 CUSTOMER-BALANCE      PIC 9(8)V99.
           05 CUSTOMER-STATUS       PIC X(10).
       
       WORKING-STORAGE SECTION.
       01  WS-EOF                   PIC X VALUE 'N'.
       01  WS-TOTAL-BALANCE         PIC 9(10)V99 VALUE ZEROS.
       01  WS-CUSTOMER-COUNT        PIC 9(5) VALUE ZEROS.
       
       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           PERFORM INITIALIZE-PROGRAM
           PERFORM PROCESS-CUSTOMERS
           PERFORM DISPLAY-SUMMARY
           STOP RUN.
       
       INITIALIZE-PROGRAM.
           OPEN INPUT CUSTOMER-FILE
           DISPLAY "CUSTOMER MANAGEMENT SYSTEM STARTED"
           DISPLAY "==================================".
       
       PROCESS-CUSTOMERS.
           PERFORM UNTIL WS-EOF = 'Y'
               READ CUSTOMER-FILE
                   AT END
                       MOVE 'Y' TO WS-EOF
                   NOT AT END
                       PERFORM CALCULATE-TOTALS
                       PERFORM VALIDATE-CUSTOMER
               END-READ
           END-PERFORM
           CLOSE CUSTOMER-FILE.
       
       CALCULATE-TOTALS.
           ADD CUSTOMER-BALANCE TO WS-TOTAL-BALANCE
           ADD 1 TO WS-CUSTOMER-COUNT.
       
       VALIDATE-CUSTOMER.
           IF CUSTOMER-EMAIL = SPACES
               DISPLAY "WARNING: Customer " CUSTOMER-ID 
                       " has no email"
           END-IF
           
           IF CUSTOMER-BALANCE < 0
               DISPLAY "ALERT: Customer " CUSTOMER-ID 
                       " has negative balance"
           END-IF.
       
       DISPLAY-SUMMARY.
           DISPLAY " "
           DISPLAY "PROCESSING SUMMARY"
           DISPLAY "=================="
           DISPLAY "Total Customers: " WS-CUSTOMER-COUNT
           DISPLAY "Total Balance: $" WS-TOTAL-BALANCE.

