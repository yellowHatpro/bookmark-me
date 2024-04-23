import {db} from "../db/db";
import {bookmarks, users} from "../db/schema";
import {eq} from "drizzle-orm";
import {User} from "../types/user";

class UserManager {
    user: User

    constructor(user: User) {
        this.user = user
    }

    public static async build(email: string): Promise<UserManager> {
        const [user] = await db
            .selectDistinct()
            .from(users)
            .where(eq(users.email, email))
        return new UserManager(user)
    }

    async setBookmarksDir(dir: string) {
        await db
            .update(users)
            .set({bookmarkDir: dir})
            .where(eq(users.email, this.user.email))
        this.user.bookmarkDir = dir
    }
}
