# Feature Specification: Comic Render Engine

**Feature Branch**: `001-comic-render-engine`

**Created**: 2026-08-11

**Status**: Draft

**Input**: User description: "Render conversations as automatically composed comic strips using an expert system for character placement, gestures, facial expressions, balloon shape, and panel layout."

## User Scenarios & Testing

### User Story 1 - Render a conversation as a comic strip (Priority: P1)

A user selects a ready-made demo dialogue or types their own messages for a small cast of
characters, and the application produces a comic strip: panels that contain the speakers with
speech balloons and facial expressions chosen automatically from the message content.

**Why this priority**: This is the core value of the feature. Without turning messages into a
rendered comic, there is no product. It proves the entire end-to-end slice: analyze messages,
decide expressions/balloons/layout, draw panels.

**Independent Test**: Fully testable by a user submitting a short scripted dialogue and visibly
receiving a comic strip made of one or more panels, without any real-time or account features.

**Acceptance Scenarios**:

1. **Given** a demo dialogue with two characters and several alternating messages, **When** the
   user asks for it to be rendered, **Then** a comic strip with at least one panel appears showing
   both characters and their messages in speech balloons.
2. **Given** a message written in ALL CAPS, **When** it is rendered, **Then** it appears in a
   shouting balloon distinct from a normal speech balloon.
3. **Given** a conversation, **When** it is rendered, **Then** each character consistently uses
   the same appearance across every panel they appear in.

---

### User Story 2 - Automatic expressions and gestures (Priority: P2)

Messages that convey emotion (joy, anger, surprise, sadness) cause the speaking character to be
drawn with a matching expression, so the comic reads emotionally without any manual styling.

**Why this priority**: Emotional rendering is what makes Comic Chat feel alive and is core to the
expert system, but it layers on top of the basic render. It is the second slice.

**Independent Test**: Fully testable by submitting messages with clear emotional keywords and
confirming the character's expression changes for messages that trigger each supported emotion,
while other aspects of the render are unchanged.

**Acceptance Scenarios**:

1. **Given** a message containing a clearly positive word such as "yay", **When** rendered,
   **Then** the speaker is drawn with a happy expression.
2. **Given** a message containing a clearly negative word such as "hate", **When** rendered,
   **Then** the speaker is drawn with an angry expression.
3. **Given** a message with no emotional signal, **When** rendered, **Then** the speaker uses a
   neutral expression.

---

### User Story 3 - Thought balloons (Priority: P3)

A message framed as an inner thought or a quiet aside is drawn in a thought balloon (cloud
bubble) instead of a speech balloon, distinguishing internal commentary from spoken lines.

**Why this priority**: Thought balloons complete the balloon vocabulary and add storytelling
range, but are a refinement over the core speech and shout balloons.

**Independent Test**: Fully testable by submitting a message marked as a thought and confirming
it renders with a thought-balloon shape distinct from speech and shout balloons. A thought is
marked by prefixing the message with the `[thought]` tag (case-insensitive, e.g. `[thought]`,
`[Thought]`), which is stripped from the displayed text.

**Acceptance Scenarios**:

1. **Given** a message prefixed `[thought]`, **When** rendered, **Then** it uses a cloud-shaped
   thought balloon with a connector tail pointing at the speaker.
2. **Given** a normal spoken message, **When** rendered, **Then** it uses a speech balloon and not
   a thought balloon.

---

### Edge Cases

- What happens when a single message has conflicting emotion signals (for example both a happy
  and an angry keyword)? The expression rule must have a defined precedence so the outcome is
  deterministic.
- How does the system handle an all-caps message that is also long? Shouting detection applies,
  and the balloon still wraps the text within the panel.
- What happens when more messages arrive than fit in one panel? The conversation splits cleanly
  across multiple panels in reading order.
- What happens when a character speaks last in one panel and first in the next? Placement must
  stay consistent to avoid the reader losing track of who is speaking.
- What happens when the user submits an empty message or a conversation with no messages? The
  render must fail gracefully with a clear message, not a malformed comic.

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept a conversation consisting of ordered messages, each assigned to
  one of the available characters.
- **FR-002**: System MUST provide a small fixed cast of characters for demo dialogue (the exact
  count and visual style are defined under Assumptions).
- **FR-003**: System MUST assign each speaking character an expression derived deterministically
  from the message content.
- **FR-004**: System MUST select a speech, thought, or shout balloon shape deterministically from
  the message content.
- **FR-005**: System MUST place speakers with consistent, deterministic positions within a panel.
- **FR-006**: System MUST split a conversation into one or more panels in reading order when the
  message count exceeds a panel's capacity.
- **FR-007**: System MUST render each character consistently (same appearance) across all panels.
- **FR-008**: System MUST produce a comic strip the user can view in a browser.
- **FR-009**: System MUST handle an empty conversation with a clear, non-crashing error response.
- **FR-010**: System MUST resolve conflicting emotion signals by a defined, documented precedence
  so output is reproducible.
- **FR-011**: System MUST provide at least one ready-made demo dialogue the user can render with
  one action.

### Key Entities

- **Character**: A participant in the conversation with a name and a single consistent visual
  identity used in every panel.
- **Message**: A single line spoken by one character, with the text and the cornerstones the
  system uses to derive balloon shape and expression.
- **Panel**: A single comic frame holding a sub-sequence of messages and the positioned characters
  who speak them.
- **Comic**: The full rendered strip consisting of one or more ordered panels.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A user can render any demo dialogue into a viewable comic strip in under 10 seconds.
- **SC-002**: Given the same conversation, the system produces the same layout and expressions on
  every render (deterministic, 100% reproducibility).
- **SC-003**: At least one of the demo dialogues is rendered correctly on the first attempt by a
  user who has never used the product (success = the expected panels, expressions, and balloons
  appear).
- **SC-004**: Every supported emotion, balloon type, and edge case in this spec is covered by an
  automated test that passes.

## Assumptions

- The first release is stateless: conversations are transient inputs and are not stored in a
  database. Persistence and real-time multi-user chat are explicitly out of scope for this
  feature.
- Rendering uses vector graphics (SVG) so the comic scales cleanly at any zoom.
- The v1 cast is three procedurally generated, stylized characters with distinct silhouettes and
  color palettes. The visual style is clean and geometric.
- Three ready-made demo dialogues are provided by default, covering surprise, a disagreement, and
  a quiet/tension exchange, to exercise shout, speech, and thought balloons.
- The expert-system rules use a core, deterministic rule set: keyword/pattern and capitalization
  driven emotion, shouted detection, balloon shape choice, two-character left/right placement by
  turn, and panel advancement by message count. Panel zoom and background props are deferred.
- Existing user authentication from the project scaffold is retained, but the demo Items CRUD
  example is removed.
- Reasonable default: conflicting emotions resolve in a fixed, documented precedence order (anger
  overrides surprise overrides joy, etc.) which is defined in the plan.