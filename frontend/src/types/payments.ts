export type StripePaymentProvider = {
  service_name: "stripe";
  api_key: string;
  publishable_key: string;
  webhook_secret: string;
};

export type MockPaymentProvider = {
  service_name: "mock";
};

export type PaymentProvider = StripePaymentProvider | MockPaymentProvider;

export type PaymentOption = {
  name: string;
  description: string;
  provider: PaymentProvider;
};

export type PaymentsConfig = {
  payment_options: {
    [uuid: string]: PaymentOption;
  };
};
