import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const add = mutation({
  args: {
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
  },
  returns: v.id("messages"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("messages", {
      sessionId: args.sessionId,
      role: args.role,
      content: args.content,
      iteration: args.iteration,
      score: args.score,
      previousScore: args.previousScore,
      nodeId: args.nodeId,
      isStreaming: args.isStreaming,
    });
  },
});

export const listBySession = query({
  args: { sessionId: v.id("sessions") },
  returns: v.array(
    v.object({
      _id: v.id("messages"),
      _creationTime: v.number(),
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
    })
  ),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("messages")
      .withIndex("by_session", (q) => q.eq("sessionId", args.sessionId))
      .order("asc")
      .collect();
  },
});

export const updateContent = mutation({
  args: {
    id: v.id("messages"),
    content: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { content: args.content });
    return null;
  },
});

export const appendContent = mutation({
  args: {
    id: v.id("messages"),
    content: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const message = await ctx.db.get(args.id);
    if (!message) {
      throw new Error("Message not found");
    }
    await ctx.db.patch(args.id, { content: message.content + args.content });
    return null;
  },
});

export const updateMetadata = mutation({
  args: {
    id: v.id("messages"),
    iteration: v.optional(v.number()),
    score: v.optional(v.number()),
    previousScore: v.optional(v.number()),
    isStreaming: v.optional(v.boolean()),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const updates: Record<string, unknown> = {};
    if (args.iteration !== undefined) updates.iteration = args.iteration;
    if (args.score !== undefined) updates.score = args.score;
    if (args.previousScore !== undefined)
      updates.previousScore = args.previousScore;
    if (args.isStreaming !== undefined) updates.isStreaming = args.isStreaming;
    await ctx.db.patch(args.id, updates);
    return null;
  },
});
