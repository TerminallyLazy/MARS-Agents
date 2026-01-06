import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const add = mutation({
  args: {
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
  },
  returns: v.id("traces"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("traces", {
      sessionId: args.sessionId,
      nodeId: args.nodeId,
      event: args.event,
      message: args.message,
      duration: args.duration,
      payload: args.payload,
    });
  },
});

export const listBySession = query({
  args: { sessionId: v.id("sessions") },
  returns: v.array(
    v.object({
      _id: v.id("traces"),
      _creationTime: v.number(),
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
    })
  ),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("traces")
      .withIndex("by_session", (q) => q.eq("sessionId", args.sessionId))
      .order("asc")
      .collect();
  },
});

export const listRecentBySession = query({
  args: {
    sessionId: v.id("sessions"),
    limit: v.number(),
  },
  returns: v.array(
    v.object({
      _id: v.id("traces"),
      _creationTime: v.number(),
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
    })
  ),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("traces")
      .withIndex("by_session", (q) => q.eq("sessionId", args.sessionId))
      .order("desc")
      .take(args.limit);
  },
});

export const clearBySession = mutation({
  args: { sessionId: v.id("sessions") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const traces = await ctx.db
      .query("traces")
      .withIndex("by_session", (q) => q.eq("sessionId", args.sessionId))
      .collect();
    for (const trace of traces) {
      await ctx.db.delete(trace._id);
    }
    return null;
  },
});
