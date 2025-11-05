---
title: Plan Changed Webhook

slug: integrations/webhooks
---

The `company.plan_change` webhook is one of the most important triggers for building sales and customer success workflows. It fires whenever a company's plan changes, whether an upgrade, downgrade, or the end of a trial period.

Some common use cases for `company.plan_changed` webhook include:
- **Identifying PLG upgrades:** Automatically notify your team or trigger automations when a self-serve customer upgrades their plan, so you can reach out to nurture and support the account.
- **Tracking trial conversions and endings:** Get alerted when a company's trial ends, enabling you to follow up or offer interventions to encourage conversion.
- **Catching downgrades:** Proactively inform Customer Success (CS) when an account downgrades, giving your team a chance to understand any pain points and try to save the account.

By listening for the `plan_changed` webhook, you can automate account lifecycle tasks and keep key teams informed about important moments in your customer journey.

## Setup

The `company.plan_change` webhook is set up like all other webhooks in Schematic. Please follow the [general webhook setup instructions](/integrations/webhooks) to create an endpoint and select the `company.plan_changed` trigger.

## Fields

All Schematic webhooks are strongly typed in each of our [SDKs](/developer_resources/sdks/overview). 

[Here](https://github.com/SchematicHQ/schematic-node/blob/764cceb36a4869565c3594692c771100545d320e/src/api/types/PlanChangeResponseData.ts#L7) is that type for our node.js SDK for reference. 

A plan can change for many reasons, the most common ones are:
1. A company proactively changes it's plan (either an upgrade or downgrade)
2. A company is on a trial that ends, and is moved to the trial expiry plan
3. A company is newly created and is put on the Initial Plan
4. A company fails to pay it's bills, and is moved to the fallback plan

To determine the cause of a plan change, there are four relevant fields provided in each webhook response: 

1. Subscription Change Action

The Subscription Change Action indicates whether the plan change is an upgrade, downgrade, or something else. Currently, a plan change is an "upgrade" if the newer plan has a higher base price; "downgrades" are determined inversely. 

In SDKs, this field is called `PlanChangeResponseDataSubscriptionChangeAction`, whereas in the raw webhook response, it can be found at `body.subscription_change_action`. 

| Value            | Explanation                                                                      |
|------------------|----------------------------------------------------------------------------------|
| `downgrade`      | The company was moved to a lower-tier plan.                                      |
| `invalid`        | The plan change was invalid or could not be recognized.                          |
| `subscribe`      | The company was assigned to a plan for the first time.                           |
| `unsubscribe`    | The company was removed from a plan and is no longer assigned any plan.          |
| `upgrade`        | The company moved to a higher-tier plan.                                         |
| `upgrade_trial`  | The company started a trial of a higher-tier plan.                               |


2. Actor Type

The Actor Type provides "who" took the action that lead to the plan change. 

In SDKs, this field is called `PlanChangeResponseDataActorType`, whereas in the raw webhook response, it can be found at `body.actor_type`.

| Value                    | Explanation                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `app_user`               | Action performed by an authenticated end user of your application.          |
| `api_key`                | Action performed by an API key or server-side integration.                  |
| `system`                 | Action automatically performed by Schematic system processes.               |
| `temporary_access_token` | Action performed in a Schematic Component (typically checkout).             |

3. Action

The Action provides an explanation for what action changed the company's plan.

In SDKs, this field is called `PlanChangeResponseDataAction`, whereas in the raw webhook response, it can be found at `body.action`.

| Value                           | Explanation                                                                                                | Likelihood                                                     |
|---------------------------------|------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| `"checkout"`                    | The company changed plans via a checkout flow.                                                             | Common                                                         |
| `"company_upsert"`              | A plan change occurred as a result of a company being created or updated (often upon company creation).    | Common                                                         |
| `"manage_plan"`                 | A plan was changed using the "Manage Plan" interface in the Schematic dashboard.                           | Common, and driven by you                                      |
| `"subscription_change"`         | The plan change resulted from a change in Stripe (e.g. non-payment, trail expiration)                      | Common                                                         |
| `"fallback_plan"`               | The company was moved to a fallback plan.                                                                  | Rare                                                    |
| `"plan_billing_product_changed"`| A plan's underlying billing product was changed, forcing a plan update for the company.                    | Rare                                                           |
| `"plan_deleted"`                | The company was moved off a plan because the plan was deleted.                                             | Rare                                                           |
| `"quickstart"`                  | The plan was set automatically via a quickstart flow (typically after onboarding).                         | Extremely rare -- only for companies created during quickstart |

    
4. Base Plan Action

The Base Plan Action value indicates why the base plan was changed. This field is often left blank. 

In SDKs, this field is called `PlanChangeResponseDataBasePlanAction`, whereas in the raw webhook response, it can be found at `body.base_plan.action`.

| Value          | Explanation                                                                                  | Likelihood |
|----------------|----------------------------------------------------------------------------------------------|------------|
| (blank)   | This means that the company was switched to a new plan (either via checkout or manage plan)                                                        | Common     |

| `"initial"`    | The company was assigned its initial base plan, typically at creation.                       | Common     |
| `"trial_expiry"` | The company’s base plan was set because a trial expired.                                   | Common     |
| `"trait"`      | The company’s plan changed because of a trait or segment update.                             | Uncommon   |
| `"fallback"`   | The company was moved to a fallback plan, often due to payment issues or plan deletion.      | Rare       |

<!-- ## Common scenarios

Below are some common scenarios that you may want to test for and which values you should expect to see in the webhook to identify them. -->

