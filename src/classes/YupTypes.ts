import {object, string, number, date, InferType, mixed} from 'yup';
import {Compilers} from './jobs/BuildJob';

// let userSchema = object({
//   name: string().required(),
//   age: number().required().positive().integer(),
//   email: string().email(),
//   website: string().url().nullable(),
//   createdOn: date().default(() => new Date()),
// });

// parse and assert validity
//let user = await userSchema.validate(await fetchUser());

//type User = InferType<typeof userSchema>;
/* {
  name: string;
  age: number;
  email?: string | undefined
  website?: string | null | undefined
  createdOn: Date
}*/

const BuildJSONSchema = object({
  kernel_config: string().required(),
  git_repo: string().required(),
  git_hash: string().required(),
  patch: string().required(),
  timeout: number().required(),
  cores: number().required(),
  metadata: string().required(),
  compiler: mixed<Compilers>().oneOf(Object.values(Compilers)).required(),
});

type _BuildJSONSchema = InferType<typeof BuildJSONSchema>;

const ReproducerJSONSchema = object({
  bzImageJobId: string().required(),
  //rootfsPath: String,
  memory: number().required(),
  boot_options: string().required(),
  reproducer: string().required(),
  //sshkeyPath: String,
  timeout: number().required(),
  cores: number().required(),
  metadata: string().required(),
});

type _ReproducerJSONSchema = InferType<typeof ReproducerJSONSchema>;

const JobIDSchema = object({
  jobid: number().required(),
});

type _JobIDSchema = InferType<typeof JobIDSchema>;

type schema =
  | typeof ReproducerJSONSchema
  | typeof BuildJSONSchema
  | typeof JobIDSchema;

export {
  schema,
  BuildJSONSchema,
  ReproducerJSONSchema,
  _BuildJSONSchema,
  _ReproducerJSONSchema,
  JobIDSchema,
  _JobIDSchema,
};
