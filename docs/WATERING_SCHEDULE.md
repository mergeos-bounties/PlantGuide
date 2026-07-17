# Watering schedule assumptions

`plantguide care schedule` estimates dates to **check the soil**, not dates on which
watering is always required. Check the species guidance before adding water.

The offline heuristic starts from the species care-card wording and adjusts the
interval using three assumptions:

- Pots under 12 cm dry faster, while pots over 20 cm retain moisture longer.
- Summer and arid conditions shorten the interval; winter and humid conditions
  lengthen it.
- Species described as moisture-loving start at a shorter interval, while
  drought-tolerant or fully-dry species start at a longer interval.

Intervals are rounded to whole days and limited to 2-30 days. The command returns
three upcoming check dates. Local light, airflow, soil mix, drainage, and plant
health can outweigh the heuristic, so inspect the soil and plant before watering.

Example:

```console
plantguide care schedule --species monstera_deliciosa --pot-cm 18 \
  --season summer --climate temperate --as-of 2026-07-17
```
