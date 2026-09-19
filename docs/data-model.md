# Data Model

Core entities:

- Story
- Character
- Event
- Relationship
- Knowledge Fact
- Timeline
- Branch
- Consequence

PostgreSQL stores structured world state.

Vector storage stores semantic source passages.

Event history records changes to alternate timelines.

Canonical state is never overwritten by generated branches.