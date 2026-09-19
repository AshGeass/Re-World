# Architecture Decisions

## Structured World State

Characters, events, relationships and timeline state are stored separately
from semantic source retrieval.

## Immutable Canon

The canonical timeline is never modified by user-generated changes.

## Branch Isolation

What-if scenarios create independent branches derived from a previous state.

## Timeline-Bounded Knowledge

Character knowledge is associated with timeline sequences so characters
cannot automatically access future information.

## Provenance

Canon, external lore and generated information are explicitly separated.