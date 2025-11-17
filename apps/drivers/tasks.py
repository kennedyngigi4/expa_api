import requests
import logging

from celery import shared_task
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction as db_transaction
from django.utils import timezone
from apps.drivers.models import Wallet, WalletTransaction
from core.utils.payments import NobukPayments


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_withdrawal_request_to_nobuk(self, transaction_id):

    try:
        with db_transaction.atomic():
            tx = WalletTransaction.objects.select_for_update().get(id=transaction_id)

            if tx.status != "pending":
                logger.info(f"Transaction {tx.id} already processed ({tx.status})")
                return

            wallet = tx.wallet
            rider = wallet.user


            # send request
            nobuk = NobukPayments(
                withdrawal_amount=tx.amount,
                withdrawal_id=tx.id,
                rider_phone=rider.phone,
                rider_name=rider.full_name
            )
            response = nobuk.Withdrawal()


            if hasattr(response, "status_code") and response.status_code == 200:
                data = response.json()
                tx.status = "completed"
                tx.processed_at = timezone.now()
                tx.save()

                # Wallet updates
                wallet.completed_deliveries_since_withdrawal = 0
                wallet.last_withdrawal = timezone.now()
                wallet.balance -= tx.amount
                wallet.save()
                
                logger.info(f"Withdrawal successful for transaction {tx.id}")
            
            else:
                tx.status = "failed"
                tx.save()
                self.retry(countdown=30)

    except WalletTransaction.DoesNotExist:
        logger.error(f"Transaction {transaction_id} not found.")

    except requests.RequestException as e:
        logger.error(f"Nobuk API error: {str(e)}")
        self.retry(countdown=60)
        
    except Exception as e:
        logger.exception(f"Unexpected error in withdrawal task: {str(e)}")







