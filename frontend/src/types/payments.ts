export interface StripePaymentProvider {
  service_name: "stripe";
  api_key: string;
  publishable_key: string;
  webhook_secret: string;
}

export interface MockPaymentProvider {
  service_name: "mock";
}

export type PaymentProvider = StripePaymentProvider | MockPaymentProvider;

export interface PaymentOption {
  name: string;
  description: string;
  provider: PaymentProvider;
}

export interface ReadPaymentOption {
  id: string;
  name: string;
  description: string;
  service_name: PaymentProvider["service_name"];
}

export interface PaymentsConfig {
  payment_options: {
    [uuid: string]: PaymentOption;
  };
}

export type PaymentStatus = "pending" | "succeeded" | "failed";
export type ProductType = "donation" | "create_membership" | "renew_membership"

export interface ReadPayment {
  id: string;
  user_id: number;
  timestamp: string;
  amount: number;
  currency: string;
  status: PaymentStatus;
  product: ProductType;
  product_description: string;
}

export interface StripeTransaction {
  transaction_type: "stripe";
  payment_id: string;
}
export interface MockTransaction {
  transaction_type: "mock";
}

export type TransactionData = StripeTransaction | MockTransaction;

export interface ReadTransaction {
  id: string;
  payment_id: string;
  data: TransactionData;
}

export interface CreateTransaction {
  provider_id: string;
  payment_id: string;
}
