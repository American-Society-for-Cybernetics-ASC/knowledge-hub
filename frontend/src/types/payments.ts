export type StripePaymentProvider = {
  provider_type: "stripe";
  stripe_api_key: string;
  stripe_publishable_key: string;
  stripe_webhook_secret: string;
};

export type PaymentProvider = StripePaymentProvider | "disabled";

export type PaymentConfig = {
  provider: StripePaymentProvider;
};
