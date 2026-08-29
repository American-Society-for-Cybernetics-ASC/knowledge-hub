import database
from database import model
from payments.module import PaymentsModule, PaymentsModuleConfig
from payments.providers.mock_provider import MockPaymentProvider
from payments.providers.stripe_provider import StripePaymentProvider

# MockPaymentProvider() or StripePaymentProvider()
PROVIDER = StripePaymentProvider()

payments = PaymentsModule()
payments.get_config()

with database.get_session() as session:
    config = PaymentsModuleConfig(provider = PROVIDER)
    config_record = session.get_one(model.Module, "payments")
    config_record.config = config.model_dump(mode = "json")
    session.commit()