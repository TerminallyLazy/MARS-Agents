import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  sessions: defineTable({
    name: v.string(),
    task: v.string(),
    status: v.union(
      v.literal("active"),
      v.literal("completed"),
      v.literal("error")
    ),
    backend: v.union(v.literal("langgraph"), v.literal("gemini")),
    iteration: v.number(),
    maxIterations: v.number(),
    isBoosted: v.boolean(),
    globalHealth: v.union(
      v.literal("healthy"),
      v.literal("degraded"),
      v.literal("critical")
    ),
    currentDraft: v.optional(v.string()),
    diagram: v.optional(v.string()),
    completedAt: v.optional(v.number()),
  }).index("by_status", ["status"]),

  messages: defineTable({
    sessionId: v.id("sessions"),
    role: v.union(
      v.literal("user"),
      v.literal("assistant"),
      v.literal("system")
    ),
    content: v.string(),
    iteration: v.optional(v.number()),
    score: v.optional(v.number()),
    previousScore: v.optional(v.number()),
    nodeId: v.optional(v.string()),
    isStreaming: v.optional(v.boolean()),
  }).index("by_session", ["sessionId"]),

  traces: defineTable({
    sessionId: v.id("sessions"),
    nodeId: v.string(),
    event: v.union(
      v.literal("start"),
      v.literal("end"),
      v.literal("error"),
      v.literal("output"),
      v.literal("custom")
    ),
    message: v.optional(v.string()),
    duration: v.optional(v.number()),
    payload: v.optional(v.string()),
  }).index("by_session", ["sessionId"]),

  nodeStates: defineTable({
    sessionId: v.id("sessions"),
    nodeId: v.string(),
    status: v.union(
      v.literal("pending"),
      v.literal("running"),
      v.literal("success"),
      v.literal("error"),
      v.literal("skipped")
    ),
    startTime: v.optional(v.number()),
    endTime: v.optional(v.number()),
    currentTask: v.optional(v.string()),
    feedback: v.optional(v.string()),
    output: v.optional(v.string()),
  })
    .index("by_session", ["sessionId"])
    .index("by_session_and_node", ["sessionId", "nodeId"]),

  scores: defineTable({
    sessionId: v.id("sessions"),
    score: v.number(),
    iteration: v.number(),
  }).index("by_session", ["sessionId"]),

  reflections: defineTable({
    sessionId: v.id("sessions"),
    iteration: v.number(),
    score: v.number(),
    reflection: v.string(),
    improvementSuggestion: v.string(),
  }).index("by_session", ["sessionId"]),
});
