import axios from 'axios'
import type { AxiosInstance } from 'axios'
import axiosRateLimit from 'axios-rate-limit';
import type { RateLimitedAxiosInstance } from 'axios-rate-limit';
// import axiosRetry from 'axios-retry'
import type { AboutInterface } from '@/interface/aboutInterface';
import type { ImageInferenceInterface } from '@/interface/imageInferenceInterface';
import { getBaseApiUrl } from './apiUrl';
import { ConcurrencyManager } from 'axios-concurrency'
import { aboutInterfaceMap } from './resToInterfaceMapper';


function getAxiosInstance(maxConcurrentRequests = 5): RateLimitedAxiosInstance | AxiosInstance {
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
  let responseData: AboutInterface = aboutInterfaceMap();
  await getAxiosInstance().get('/info/about').then((res) => {
    responseData = aboutInterfaceMap(res.data)
  })
  return responseData
}

// One shared client for image uploads so the concurrency limit applies across
// every image dropped at once (a fresh instance per call would not be limited).
let uploadClient: RateLimitedAxiosInstance | AxiosInstance | null = null

export function inferenceImage(file: File): Promise<ImageInferenceInterface> {
  if (uploadClient === null) {
    uploadClient = getAxiosInstance(3)
  }
  const form = new FormData()
  form.append('file', file, file.name)
  return uploadClient
    .post('/model/inference_image', form)
    .then(res => res.data as ImageInferenceInterface)
}
