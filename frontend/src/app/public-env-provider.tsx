'use client'
 
import { createContext } from 'react'
 
export interface PublicEnvironmentVariables {
  backendUrl: string,
}

export const PublicEnv = createContext<PublicEnvironmentVariables>({
  backendUrl: "",
})
 
export default function PublicEnvProvider({
    publicEnv,
    children,
}: {
  publicEnv: PublicEnvironmentVariables,
  children: React.ReactNode
}) {
  return <PublicEnv.Provider value={publicEnv}>{children}</PublicEnv.Provider>
}