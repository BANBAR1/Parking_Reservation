# Parking Reservation

A learning project: a small Python app for modeling parking reservations (spots, drivers, bookings) and calculating cost. There is currently no way to actually book a spot end-to-end — it's models and a cost calculation, not a full application yet.

![checks](https://github.com/BANBAR1/Parking_Reservation/actions/workflows/checks.yml/badge.svg)

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Setup

```bash
uv sync
```

## Run

```bash
uv run python -m parking_reservation
```

## Test

```bash
uv run pytest
```

## Project layout

```
src/
  parking_reservation/
    models/
    pricing.py
tests/
pyproject.toml
```

The package lives under `src/` rather than at the repo root — this keeps the installed package isolated from the project's own files (tests, config), so you can't accidentally import an uninstalled version of the code just because you happen to be running Python from the repo root.

## Contributing

- `main` is protected — no direct commits. All work happens on a branch and comes back in through a reviewed Pull Request.
- Branch names follow `<type>-<short-description>`, e.g. `feature-add-payment-model`, `fix-booking-date-bug`. Allowed types: `feature`, `fix`, `chore`, `docs`.
- One thing per branch/PR — don't mix an unrelated fix into a feature branch.
- PRs need at least one approval before merging, and merge as a single squashed commit onto `main`.

See [#5](https://github.com/BANBAR1/Parking_Reservation/issues/5) for the full branching workflow.

## Hourly rate location

The hourly rate is captured on the Booking at creation time rather than looked up later when the cost is calculated. That freezes the price the driver agreed to, so a later change to the default rates cannot silently rewrite an existing booking.
