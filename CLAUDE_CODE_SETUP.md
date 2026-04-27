# CLAUDE_CODE_SETUP.md — getting Claude Code productive on this codebase

This is the one-time setup. Once done, every Claude Code session loads the right knowledge automatically.

---

## Why this matters

Claude is fluent in Python and Vue, but it doesn't reliably know Frappe's quirks: how `frappe.utils` imports break inside Server Scripts, what's permitted in `validate` vs `before_save`, when to use `frappe.db.set_value` vs `doc.db_set`, why `frappe.get_all` ignores permissions while `frappe.get_list` respects them. Without guidance, you'll get code that *looks* right and **fails in production**.

The fix: install the **OpenAEC Frappe Claude Skill Package** (61 deterministic skills, ~95% Frappe surface area, version-aware for v16). Claude reads them automatically before generating code. Errors drop sharply.

---

## Step 1 — Install Claude Code

If you don't have it:

```bash
# macOS / Linux
curl -fsSL https://claude.ai/install.sh | sh

# Or via npm
npm install -g @anthropic-ai/claude-code
```

Verify:

```bash
claude --version
```

---

## Step 2 — Install the OpenAEC Frappe Skill Package

Clone and copy:

```bash
# Clone the package (anywhere outside your bench)
cd ~
git clone https://github.com/OpenAEC-Foundation/Frappe_Claude_Skill_Package.git

# Copy all 61 skills into Claude Code's skills directory
mkdir -p ~/.claude/skills
cp -r Frappe_Claude_Skill_Package/skills/source/* ~/.claude/skills/

# Verify
ls ~/.claude/skills | head -20
```

You should see folders like `frappe-syntax-controllers`, `frappe-core-permissions`, `frappe-impl-migrations`, etc. There are 61 of them.

These skills are deterministic — Claude doesn't decide "should I use this?" Claude reads the relevant `SKILL.md` whenever it touches the matching topic. Your job is just to make them available.

---

## Step 3 — Pin Frappe v16

Both this app and the skill package target Frappe v14–v16. We use **v16 only**. Add this to the project root in a file Claude reads first:

`.claude/project.md` (Claude Code reads this on every session in the workspace):

```markdown
# Project context — alumni

## Versions (pin everything)

- Frappe: **v16+ ONLY**. Do not generate code that targets v14 or v15.
- Use v16-specific features when applicable:
  - `autoname: "uuid"` for new DocTypes that don't need a human-readable ID
  - Type annotations on all controller methods
  - `frappe.utils.data_masker` for PII fields (phone, email) when masking is required
  - Virtual DocTypes for read-only views over external data
  - The improved scheduler's `cron` events
- Python: 3.11+
- Node: 20 LTS

## Skill package

The OpenAEC Frappe Skill Package is installed at `~/.claude/skills/`.
Skills relevant to this app cover: doctype creation, controllers, hooks,
permissions, REST API, migrations, fixtures, scheduler, jinja, print formats,
testing, deployment.

When generating Frappe code, defer to the skill if it exists.
```

Commit `.claude/project.md` to the repo so every team member benefits.

---

## Step 4 — Wire the project files

These four files matter for every session:

| File | Purpose | Claude reads |
|---|---|---|
| `CLAUDE.md` | Conventions, hard rules, naming, forbidden patterns | Auto on session start |
| `SPEC.md` | Canonical reference for every doctype/field/workflow | When asked, or paste relevant section |
| `INTEGRATIONS.md` | Adapter contracts | When you touch any cross-app boundary |
| `BUILD_TICKETS.md` | Backlog | Pull next ticket each session |

You don't need to paste these every session. With `CLAUDE.md` at the repo root, Claude Code finds it automatically.

---

## Step 5 — Test the setup

Open a new Claude Code session in the repo:

```bash
cd ~/frappe-bench/apps/alumni
claude
```

Type:

> "Create a stub DocType called `Alumni Test Doc` with a `Data` field `title` and a `Long Text` field `body`. Use Frappe v16 conventions including type annotations on the controller."

Claude should:

1. Ask which folder under `alumni/doctype/`.
2. Create the DocType JSON correctly (with `engine: "InnoDB"`, `module: "Alumni"`, etc.).
3. Generate `alumni_test_doc.py` with type annotations: `def validate(self) -> None: ...`.
4. Create the test file.
5. Run `bench migrate` if you ask.

If any of those go wrong, the skill package isn't being loaded. Re-check Step 2.

---

## Daily workflow

### Start of session

1. `cd` into the repo.
2. Run `claude`.
3. (Optional) paste:
   ```
   Read CLAUDE.md, SPEC.md (relevant section), and PROJECT_STATE.md.
   I'm working on ticket T-XXX from BUILD_TICKETS.md.
   ```
4. Let Claude write code + tests.

### One ticket = one session

Pick the topmost unchecked ticket from `BUILD_TICKETS.md`. Resist the urge to do two at once. Claude is most accurate on focused, sized work.

### Diff review

After Claude commits, run:

```bash
git diff --stat
git diff
```

If you spot anything off, prompt:

> "I see [thing]. The convention in CLAUDE.md says [rule]. Please fix."

Claude will revise without ego.

### PR review with a fresh Claude

Open Claude.ai web, paste the diff, prompt:

> "Review this PR for Frappe anti-patterns, security holes, missing permissions checks, and any cross-app imports outside `alumni/integrations/`. Be ruthless."

Fresh-context review catches things the building Claude missed.

### End of session

Update `PROJECT_STATE.md` with:
- What shipped (commit hashes)
- New blockers
- Next 3 tickets

---

## Common pitfalls (and how to avoid them)

| Pitfall | Fix |
|---|---|
| Claude generates `from frappe.utils import nowdate` inside a Server Script | Skill package catches this; if it slips, prompt: "Server Scripts block all imports — use `frappe.utils.nowdate()` directly." |
| Claude forgets that `frappe.get_all` ignores permissions | Prompt: "Use `frappe.get_list` so permission filters apply." |
| Claude uses `Float` for currency | Prompt: "Use `Currency` field type per CLAUDE.md forbidden patterns." |
| Claude bypasses the adapter and imports from `erpnext` directly | The CI guard `tests/test_no_cross_app_imports.py` will fail. Prompt: "Move this through `alumni.integrations.receivables`." |
| Claude generates v15 code | Prompt: "Use v16 features per `.claude/project.md`." |
| Claude writes a giant 500-line PR | Stop. Say: "Split this into 3 PRs by [feature boundary]." |

---

## Power moves

### `--continue` for long tickets

If a ticket spans multiple files and Claude hits its context budget, use `--continue` to resume in a follow-up session with state preserved.

### `/skills` slash command

Inside Claude Code, type `/skills` to see which Frappe skills are loaded. If a topic seems missing, you can browse `~/.claude/skills/` directly to confirm.

### Custom slash commands for your project

Add `.claude/commands/` files for repeatable patterns:

```markdown
# .claude/commands/new-doctype.md

When the user types `/new-doctype <name>`:
1. Ask which module folder
2. Generate DocType JSON with v16 conventions:
   - autoname (uuid or hash)
   - type annotations on controller
   - test file in tests/
3. Add to fixtures if it's a configuration DocType
4. Update SPEC.md §03
5. Run bench migrate
```

Then in any session: `/new-doctype Alumni Foo` — Claude follows the playbook.

---

## Updating the skill package

Pull updates monthly:

```bash
cd ~/Frappe_Claude_Skill_Package
git pull origin main
cp -r skills/source/* ~/.claude/skills/
```

Releases follow Frappe versions. v3.x targets Frappe v14–v16.

---

## Beyond this app — agent skills for the team

When you onboard a new dev, the same setup is one command:

```bash
git clone https://github.com/OpenAEC-Foundation/Frappe_Claude_Skill_Package.git ~/Frappe_Claude_Skill_Package
mkdir -p ~/.claude/skills
cp -r ~/Frappe_Claude_Skill_Package/skills/source/* ~/.claude/skills/
```

Their Claude Code now generates correct Frappe code from day one. No tribal knowledge transfer needed.

---

## Reference

- OpenAEC Frappe Skill Package: <https://github.com/OpenAEC-Foundation/Frappe_Claude_Skill_Package>
- Skill package docs: `INDEX.md`, `USAGE.md`, `WAY_OF_WORK.md`, `LESSONS.md` in that repo
- Buzz event app: <https://github.com/BuildWithHussain/buzz>
- Frappe v16 changelog: <https://github.com/frappe/frappe/releases> (filter v16.x)
