import {integer, pgTable, serial, text} from "drizzle-orm/pg-core";
import {relations} from "drizzle-orm";

export const users = pgTable("users",{
    id: serial("id").primaryKey(),
    name: text("name").notNull(),
    email: text("email").notNull(),
    bookmarkDir: text("bookmark_dir").notNull()
})

export const bookmarks = pgTable("bookmarks", {
    id: serial("id").primaryKey(),
    userId: integer("user_id").notNull(),
    title: text("title").notNull(),
    url: text("url").notNull()
})

export const usersRelations = relations(users,({ many })=> ({
    bookmarks: many(bookmarks)
}))

export const bookmarksRelations = relations(bookmarks, ({ one }) => ({
    user: one(users, {
        fields: [bookmarks.userId],
        references: [users.id]
    })
}))

export const schema = {
    bookmarks,
    users,
    usersRelations,
    bookmarksRelations
}