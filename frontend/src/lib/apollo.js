import { ApolloClient, InMemoryCache, createHttpLink, gql } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'

export const TOKEN_KEY = 'academico_jwt_token'

const httpLink = createHttpLink({
  uri: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/graphql',
})

const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem(TOKEN_KEY)

  return {
    headers: {
      ...headers,
      authorization: token ? `JWT ${token}` : '',
    },
  }
})

export const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
})

export const LOGIN_MUTATION = gql`
  mutation Login($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
      token
      payload
      refreshExpiresIn
    }
  }
`

export const DASHBOARD_RESUMEN_QUERY = gql`
  query DashboardResumen {
    dashboardResumen {
      totalEstudiantes
      totalDocentes
      totalProyectos
      totalMaterias
      promedioPpaEstudiantes
    }
  }
`

export const loginWithCredentials = async (username, password) => {
  const { data } = await client.mutate({
    mutation: LOGIN_MUTATION,
    variables: { username, password },
  })

  const token = data?.tokenAuth?.token

  if (!token) {
    throw new Error('No se recibió el token JWT del servidor.')
  }

  localStorage.setItem(TOKEN_KEY, token)

  return data.tokenAuth
}
