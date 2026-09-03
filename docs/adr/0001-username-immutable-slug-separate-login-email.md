# Username is a public, immutable slug; login uses a separate private email

We considered making Username double as the login identifier, since it's already unique per User and would mean one less field to manage. We instead decided to authenticate Users by a private Login Email, keeping Username purely as the fixed public slug for the Portfolio URL (`/username`). This decouples the identifier used to log in — which never needs to be memorable, shareable, or stable — from the identifier used to share and bookmark a Portfolio, which must never change once a link has been shared.

## Considered Options

- **Username as login identifier**: one fewer field to manage, but ties account login/recovery to a value that must also stay stable forever for URL purposes, and forces a Login Email to be added later anyway if password-reset-by-email is ever introduced.
- **Login Email as login identifier, Username as a separate immutable public slug (chosen)**: keeps the two concerns independent; Username can be optimized purely for readability and shareability without login constraints, and password-reset-by-email is trivial to add later.
