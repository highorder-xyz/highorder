import {format} from '../src/common/utils'

test("Advance Change Object", () => {
  expect(
    format("Your name is {name} and you have {age} years old!",
    {
      name: "名字",
      age: 21,
    })
  ).toEqual("Your name is 名字 and you have 21 years old!");
});

test("Advanced object change position", () => {
    expect(
      format("Your name is {info.name} and you have {age} years old!",
      {
        info:{
            name: "名字"
        },
        age: 21,
      })
    ).toEqual("Your name is 名字 and you have 21 years old!");
  });

