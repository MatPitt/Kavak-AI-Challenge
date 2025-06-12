from app.core.config import Config
import numpy as np
from datetime import datetime
from app.core.logger import app_logger, error_logger

class FinancingService:
    def __init__(self):
        self.interest_rate = Config.INTEREST_RATE
        self.min_term = Config.MIN_TERM
        self.max_term = Config.MAX_TERM
        app_logger.info("Initialized FinancingService with interest rate: %.2f%%, terms: %d-%d months",
                       self.interest_rate * 100, self.min_term, self.max_term)

    def calculate_monthly_payment(self, principal, term_months):
        """
        Calcula el pago mensual para un préstamo.
        
        Args:
            principal (float): Monto del préstamo
            term_months (int): Plazo en meses
            
        Returns:
            float: Pago mensual
        """
        try:
            app_logger.info("Calculating monthly payment for principal: %.2f, term: %d months",
                          principal, term_months)
            
            if term_months < self.min_term or term_months > self.max_term:
                error_msg = f"El plazo debe estar entre {self.min_term} y {self.max_term} meses"
                app_logger.warning(error_msg)
                raise ValueError(error_msg)
            
            monthly_rate = self.interest_rate / 12
            payment = (principal * monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
            
            app_logger.info("Calculated monthly payment: %.2f", payment)
            return payment
            
        except Exception as e:
            error_logger.error("Error calculating monthly payment: %s", str(e), exc_info=True)
            raise

    def calculate_amortization_schedule(self, car_price, down_payment, term_months):
        """
        Calcula la tabla de amortización para un préstamo.
        
        Args:
            car_price (float): Precio del auto
            down_payment (float): Enganche
            term_months (int): Plazo en meses
            
        Returns:
            dict: Información del financiamiento
        """
        try:
            app_logger.info("Calculating amortization schedule for car price: %.2f, down payment: %.2f, term: %d months",
                          car_price, down_payment, term_months)
            
            # Validar enganche
            if down_payment >= car_price:
                error_msg = "El enganche no puede ser mayor o igual al precio del auto"
                app_logger.warning(error_msg)
                raise ValueError(error_msg)
            
            # Calcular monto del préstamo
            loan_amount = car_price - down_payment
            app_logger.debug("Loan amount: %.2f", loan_amount)
            
            # Calcular pago mensual
            monthly_payment = self.calculate_monthly_payment(loan_amount, term_months)
            
            # Calcular tabla de amortización
            balance = loan_amount
            schedule = []
            
            for month in range(1, term_months + 1):
                interest_payment = balance * (self.interest_rate / 12)
                principal_payment = monthly_payment - interest_payment
                balance -= principal_payment
                
                schedule.append({
                    'month': month,
                    'payment': round(monthly_payment, 2),
                    'principal': round(principal_payment, 2),
                    'interest': round(interest_payment, 2),
                    'balance': round(balance, 2)
                })
            
            total_interest = sum(payment['interest'] for payment in schedule)
            total_payment = monthly_payment * term_months
            
            result = {
                'car_price': car_price,
                'down_payment': down_payment,
                'loan_amount': loan_amount,
                'term_months': term_months,
                'monthly_payment': round(monthly_payment, 2),
                'total_interest': round(total_interest, 2),
                'total_payment': round(total_payment, 2),
                'schedule': schedule
            }
            
            app_logger.info("Successfully calculated amortization schedule. Total interest: %.2f, Total payment: %.2f",
                          total_interest, total_payment)
            return result
            
        except Exception as e:
            error_logger.error("Error calculating amortization schedule: %s", str(e), exc_info=True)
            return None 