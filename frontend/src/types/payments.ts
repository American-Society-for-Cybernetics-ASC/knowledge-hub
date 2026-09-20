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

export interface PaymentsConfig {
  payment_options: {
    [uuid: string]: PaymentOption;
  };
}

export type PaymentStatus = "pending" | "succeeded" | "failed";

export interface RenewMembershipProduct {
  product: "renew_membership";
  user_id: number;
  duration: number;
}

export interface CreateMembershipProduct {
  product: "create_membership";
  user_id: number;
  duration: number;
  membership_type_id: string;
}

export interface DonationProduct {
  product: "donation";
}

export type ProductTypes =
  RenewMembershipProduct | CreateMembershipProduct | DonationProduct;

export interface ReadPayment {
  id: string;
  user_id: number;
  time: string;
  amount: number;
  currency: string;
  status: PaymentStatus;
  product: ProductTypes;
}

export interface StripeTransaction {
  transaction_type: "stripe";
  payment_id: string;
}
export interface MockTransaction {
  transaction_type: "mock";
}

export type TransactionData = StripeTransaction | MockTransaction;
