import { createAsyncThunk } from "@reduxjs/toolkit";
import { selectConfig } from "../configSlice";
import { selectCredential } from "../credentialSlice";
import { RootState } from "../rootReducer";

interface Course {
    id: number;
    name: string;
    grade: number;
}

export const fetchCourses = createAsyncThunk<
    Course[],
    void,
    { state: RootState }
>("courses/fetchCourses", async (_, thunkAPI) => {
    const { username, password } = selectCredential(thunkAPI.getState());
    const backendUrl =
        selectConfig(thunkAPI.getState()).backendUrl || "localhost:65535";
    try {
        const res = await fetch(
            `http://${backendUrl}/courses?username=${username}&password=${password}`
        );
        const data = await res.json();

        if (res.ok) {
            return data;
        } else {
            return thunkAPI.rejectWithValue(data);
        }
    } catch (error: any) {
        return thunkAPI.rejectWithValue({
            error: error.message || String(error),
        });
    }
});
