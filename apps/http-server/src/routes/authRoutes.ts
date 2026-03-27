import { Router } from "express";
import { userRegisterController } from "../controllers/authController";


const router:Router = Router();


router.post("/register", userRegisterController)






export default  router