import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "./store";

type CurrentCourseState = string;

const initialState: CurrentCourseState = "";

const currentCourseSlice = createSlice({
    name: "currentCourse",
    initialState,
    reducers: {
        setCurrentCourse: (state, action: PayloadAction<string>) => {
            return action.payload;
        },
    },
});

export const { setCurrentCourse } = currentCourseSlice.actions;

export const selectCurrentCourse = (state: RootState) => state.currentCourse;

export default currentCourseSlice.reducer;
