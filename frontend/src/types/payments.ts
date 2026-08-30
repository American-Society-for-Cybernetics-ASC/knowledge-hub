export type StripePaymentProvider = {
  provider_type: "stripe";
  api_key: string;
  publishable_key: string;
  webhook_secret: string;
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
