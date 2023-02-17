import { combineReducers } from "@reduxjs/toolkit";
import credentialReducer from "./credentialSlice";
import configReducer from "./configSlice";
import currentCourseReducer from "./currentCourseSlice";

const rootReducer = combineReducers({
    credential: credentialReducer,
    config: configReducer,
    currentCourse: currentCourseReducer,
});

export type RootState = ReturnType<typeof rootReducer>;
export default rootReducer;
