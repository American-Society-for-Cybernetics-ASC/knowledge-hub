'use client'
 
import { createContext } from 'react'
 
export interface PublicEnvironmentVariables {
  backendUrl: string,
}

export const PublicEnv = createContext<PublicEnvironmentVariables>({
  backendUrl: "",
})
 
/**
 * The frontend does not have access to environment variables. This sets up a context that
 * allows us to expose a subset that are safe to pass over.
 */
export default function PublicEnvProvider({
    children,
}: {
  children: React.ReactNode
}) {
  return <PublicEnv.Provider value={{backendUrl: process.env.BACKEND_URL || ""}}>
    {children}
  </PublicEnv.Provider>
}