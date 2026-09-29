from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TraceEvaluation:
  tool_calls: tuple[str, ...]
  missing_required: tuple[str, ...]
  forbidden_present: tuple[str, ...]

  @property
  def passed(self) -> bool:
    return not self.missing_required and not self.forbidden_present


def extract_tool_calls(events: Iterable[object]) -> tuple[str, ...]:
  """Extracts function-call tool names from ADK events in order."""

  tool_calls = []
  for event in events:
    content = getattr(event, "content", None)
    for part in getattr(content, "parts", []) or []:
      function_call = getattr(part, "function_call", None)
      name = getattr(function_call, "name", None)
      if name:
        tool_calls.append(name)
  return tuple(tool_calls)


def evaluate_tool_trace(
  events: Iterable[object],
  required_tool_calls: Iterable[str] = (),
  forbidden_tool_calls: Iterable[str] = (),
) -> TraceEvaluation:
  tool_calls = extract_tool_calls(events)
  observed = set(tool_calls)
  required = tuple(required_tool_calls)
  forbidden = tuple(forbidden_tool_calls)

  return TraceEvaluation(
    tool_calls=tool_calls,
    missing_required=tuple(name for name in required if name not in observed),
    forbidden_present=tuple(name for name in forbidden if name in observed),
  )