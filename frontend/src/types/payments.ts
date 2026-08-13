export type StripePaymentProvider = {
  provider_type: "stripe";
  stripe_api_key: string;
  stripe_publishable_key: string;
  stripe_webhook_secret: string;
};

export type PaymentProvider = StripePaymentProvider;

export type PaymentOption = {
  name: string;
  description: string;
  provider: PaymentProvider;
};

export type PaymentsConfig = {
  payment_options: PaymentOption[];
};
