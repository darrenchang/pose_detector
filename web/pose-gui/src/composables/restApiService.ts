import axios from 'axios'
import type { AxiosResponse } from 'axios'
import axiosRateLimit, { RateLimitedAxiosInstance } from 'axios-rate-limit';
import axiosRetry from 'axios-retry'
import type { AboutInterface } from '@/interface/aboutInterface';
import { getBaseApiUrl } from './apiUrl';
import { ConcurrencyManager } from 'axios-concurrency'
import { aboutInterfaceMap } from './resToInterfaceMapper';


function getAxiosInstance(maxConcurrentRequests = 5) {
  let apiUrl = getBaseApiUrl()
  const instance = axiosRateLimit(axios.create({
    baseURL: apiUrl,
  }), {
    maxRequests: 1,
    perMilliseconds: 50,
  })
  ConcurrencyManager(instance, maxConcurrentRequests)
  return instance
}

export async function getInfo(): Promise<AboutInterface> {
  let responseData = aboutInterfaceMap();
  await getAxiosInstance().get('/info/about').then((res: AxiosResponse) => {
    responseData = aboutInterfaceMap(res)
  })
  return responseData
}
