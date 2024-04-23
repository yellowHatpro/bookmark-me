import {db} from "../db/db";
import {bookmarks} from "../db/schema";
import {eq} from "drizzle-orm";

class BookmarkManager{
    bookmarks: Bookmark[]

    constructor(bookmarks: Bookmark[]) {
        this.bookmarks = bookmarks
    }

    public static async build(): Promise<BookmarkManager> {
        const res = await db.select().from(bookmarks)
        return new BookmarkManager(res)
    }

    async addBookmark(title: string, user_id: number, url: string) {
        await db
            .insert(bookmarks)
            .values({title: title, userId: user_id, url: url})
    }

    async deleteBookmark(id: number) {
        await db
            .delete(bookmarks)
            .where(eq(bookmarks.id, id))
    }
}