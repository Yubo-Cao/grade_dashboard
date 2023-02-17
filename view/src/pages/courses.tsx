import CourseCard from "@/components/CourseCard";
import { selectCredential } from "@/store/credentialSlice";
import { selectCurrentCourse, setCurrentCourse } from "@/store/currentCourseSlice";
import { useAppDispatch, useAppSelector } from "@/store/store";
import Async from "react-async";
import RootLayout from "./layout";

const loadCourses = async (
  username: string | undefined,
  password: string | undefined
) => {
  if (!username || !password) return Promise.reject("No username or password");
  const res = await fetch(
    `http://localhost:65535/courses?username=${username}&password=${password}`
  );
  if (!res.ok) {
    return Promise.reject("Invalid username or password");
  }
  const data = await res.json();
  return data.map((course: any) => {
    let { course: name, teacher, grade, id, email } = course;
    return {
      name: name.split(": ")[1],
      teacher,
      score: parseInt(grade),
      id,
      email,
    };
  });
};

function CourseSelection() {
  const { username, password } = useAppSelector(selectCredential);
  const dispatch = useAppDispatch();
  return (
    <div className="grid-flow gap-8 w-full place-items-center">
      <Async promiseFn={() => loadCourses(username, password)}>
        {({ data, error, isLoading }) => {
          if (isLoading)
            return Array(7)
              .fill(0)
              .map((_, i) => (
                <div
                  className="animate-pulse w-64 h-64 bg-slate-50"
                  key={i}
                ></div>
              ));
          if (error) {
            return <p>Something went wrong: {String(error)}</p>;
          }
          if (data)
            return data.map((course: any) => (
              <CourseCard
                key={course.id}
                {...course}
                onClick={() => dispatch(setCurrentCourse(course.id))}
              />
            ));
        }}
      </Async>
    </div>
  );
}

type ActionType =
  | "grade_book"
  | "blame"
  | "contrib"
  | "total_score"
  | "meta"
  | "comments"
  | "measure_types"
  | "score_by_type";

async function loadCourse(id: string, action: ActionType | ActionType[]) {
  //
}

function FocusCourse() {
  const currentCourse = useAppSelector(selectCurrentCourse);
}

export default function Courses() {
  return (
    <RootLayout>
      <CourseSelection />
    </RootLayout>
  );
}
