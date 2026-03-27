
import { Request, Response } from "express"
import { prisma } from "@repo/db"
import bcrypt from 'bcrypt'
import jwt from "jsonwebtoken"
import { errorResponse } from "../utils/error"

export const userRegisterController = async (req: Request, res: Response) => {

    try {

        const { name, email, password } = req.body;

        console.log( "The name , email and passwords are: ", name, email, password)

        // is user existed already
        const isUserExisted = await prisma.user.findUnique({
            where: { email }
        })

        if (isUserExisted) {
            return errorResponse(res, 400, "Email is already existed..")
        }

        const hashedPassword = await bcrypt.hash(password, 10);


        const user = await prisma.user.create({
            data: {
                name,
                password: hashedPassword,
                email
            }
        });

        // generating token...
        const token = jwt.sign({
            userId: user.id
        }, process.env.JWT_SECRET || "secret", { expiresIn: '7d' });

        return res.status(201).json({
            token,
            user: {
                id: user.id,
                email: user.email,
                name: user.name
            }
        })

    } catch (error) {
        console.log("signupError", error)
        return errorResponse(res, 500, "Internal Server Error...")

    }

}