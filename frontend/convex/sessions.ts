import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const create = mutation({
  args: {
    name: v.string(),
    task: v.string(),
    backend: v.union(v.literal("langgraph"), v.literal("gemini")),
    maxIterations: v.number(),
  },
  returns: v.id("sessions"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("sessions", {
      name: args.name,
      task: args.task,
      status: "active",
      backend: args.backend,
      iteration: 0,
      maxIterations: args.maxIterations,
      isBoosted: false,
      globalHealth: "healthy",
    });
  },
});

export const get = query({
  args: { id: v.id("sessions") },
  returns: v.union(
    v.object({
      _id: v.id("sessions"),
      _creationTime: v.number(),
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
    }),
    v.null()
  ),
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

export const list = query({
  args: {},
  returns: v.array(
    v.object({
      _id: v.id("sessions"),
      _creationTime: v.number(),
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
    })
  ),
  handler: async (ctx) => {
    return await ctx.db.query("sessions").order("desc").collect();
  },
});

export const listActive = query({
  args: {},
  returns: v.array(
    v.object({
      _id: v.id("sessions"),
      _creationTime: v.number(),
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
    })
  ),
  handler: async (ctx) => {
    return await ctx.db
      .query("sessions")
      .withIndex("by_status", (q) => q.eq("status", "active"))
      .order("desc")
      .collect();
  },
});

export const updateStatus = mutation({
  args: {
    id: v.id("sessions"),
    status: v.union(
      v.literal("active"),
      v.literal("completed"),
      v.literal("error")
    ),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const updates: Record<string, unknown> = { status: args.status };
    if (args.status === "completed" || args.status === "error") {
      updates.completedAt = Date.now();
    }
    await ctx.db.patch(args.id, updates);
    return null;
  },
});

export const updateIteration = mutation({
  args: {
    id: v.id("sessions"),
    iteration: v.number(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { iteration: args.iteration });
    return null;
  },
});

export const updateDraft = mutation({
  args: {
    id: v.id("sessions"),
    currentDraft: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { currentDraft: args.currentDraft });
    return null;
  },
});

export const updateDiagram = mutation({
  args: {
    id: v.id("sessions"),
    diagram: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { diagram: args.diagram });
    return null;
  },
});

export const updateHealth = mutation({
  args: {
    id: v.id("sessions"),
    globalHealth: v.union(
      v.literal("healthy"),
      v.literal("degraded"),
      v.literal("critical")
    ),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { globalHealth: args.globalHealth });
    return null;
  },
});

export const setBoosted = mutation({
  args: {
    id: v.id("sessions"),
    isBoosted: v.boolean(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { isBoosted: args.isBoosted });
    return null;
  },
});

export const remove = mutation({
  args: { id: v.id("sessions") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const messages = await ctx.db
      .query("messages")
      .withIndex("by_session", (q) => q.eq("sessionId", args.id))
      .collect();
    for (const msg of messages) {
      await ctx.db.delete(msg._id);
    }

    const traces = await ctx.db
      .query("traces")
      .withIndex("by_session", (q) => q.eq("sessionId", args.id))
      .collect();
    for (const trace of traces) {
      await ctx.db.delete(trace._id);
    }

    const nodeStates = await ctx.db
      .query("nodeStates")
      .withIndex("by_session", (q) => q.eq("sessionId", args.id))
      .collect();
    for (const ns of nodeStates) {
      await ctx.db.delete(ns._id);
    }

    const scores = await ctx.db
      .query("scores")
      .withIndex("by_session", (q) => q.eq("sessionId", args.id))
      .collect();
    for (const score of scores) {
      await ctx.db.delete(score._id);
    }

    const reflections = await ctx.db
      .query("reflections")
      .withIndex("by_session", (q) => q.eq("sessionId", args.id))
      .collect();
    for (const ref of reflections) {
      await ctx.db.delete(ref._id);
    }

    await ctx.db.delete(args.id);
    return null;
  },
});
