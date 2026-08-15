import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Loader2, Plus, RefreshCcw, Trash2, Wand2 } from "lucide-react"
import { useEffect, useRef } from "react"
import { useFieldArray, useForm } from "react-hook-form"
import { z } from "zod"

import {
  type ComicInstruction,
  type ComicMessage,
  ComicService,
  type DemoDialogue,
} from "@/client"
import ComicStrip from "@/components/Comic/ComicStrip"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const SPEAKERS = ["ada", "bob", "cara"]

const messageSchema = z.object({
  speaker_id: z.string().min(1, { message: "Pick a speaker" }),
  text: z
    .string()
    .trim()
    .min(1, { message: "Message can't be empty" })
    .max(500, { message: "Message must be at most 500 characters" }),
})

const formSchema = z.object({
  messages: z
    .array(messageSchema)
    .min(1, { message: "Add at least one message" }),
})

type FormData = z.infer<typeof formSchema>

const demosQueryOptions = {
  queryKey: ["comic-demos"],
  queryFn: () => ComicService.listDemos().then((response) => response.data),
}

export const Route = createFileRoute("/_layout/comic")({
  component: Comic,
  head: () => ({
    meta: [
      {
        title: "Comic - FastAPI Template",
      },
    ],
  }),
})

function Comic() {
  const { showErrorToast } = useCustomToast()
  const demosQuery = useQuery(demosQueryOptions)
  const lastMessages = useRef<ComicMessage[] | null>(null)

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: { messages: [{ speaker_id: "ada", text: "" }] },
  })
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "messages",
  })

  const renderMutation = useMutation({
    mutationFn: (messages: ComicMessage[]) =>
      ComicService.renderComic({ body: { messages } }),
    onError: handleError.bind(showErrorToast),
  })
  const comic: ComicInstruction | null = renderMutation.data?.data.comic ?? null

  const renderMessages = (messages: ComicMessage[]) => {
    lastMessages.current = messages
    renderMutation.mutate(messages)
  }

  const onSubmit = (data: FormData) => {
    renderMessages(data.messages)
  }

  const loadDemo = (demo: DemoDialogue) => {
    form.reset({ messages: demo.messages.map((message) => ({ ...message })) })
    renderMessages(demo.messages)
  }

  const retry = () => {
    if (lastMessages.current) {
      renderMutation.mutate(lastMessages.current)
    }
  }

  useEffect(() => {
    if (!demosQuery.data) {
      return
    }
    const first = demosQuery.data.demos[0]
    if (first) {
      form.reset({
        messages: first.messages.map((message) => ({ ...message })),
      })
    }
  }, [demosQuery.data, form.reset])

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Comic</h1>
        <p className="text-muted-foreground">
          Turn a conversation into a comic strip
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Demo dialogues</CardTitle>
          <CardDescription>
            Render a ready-made dialogue with one click
          </CardDescription>
        </CardHeader>
        <CardContent>
          {demosQuery.isPending ? (
            <div className="flex flex-col gap-2">
              <Skeleton className="h-9 w-48" />
              <Skeleton className="h-9 w-48" />
              <Skeleton className="h-9 w-48" />
            </div>
          ) : demosQuery.isError ? (
            <Alert variant="destructive">
              <Loader2 />
              <AlertTitle>Couldn't load demos</AlertTitle>
              <AlertDescription className="flex flex-col items-start gap-2">
                <span>
                  Something went wrong while fetching the demo dialogues.
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => demosQuery.refetch()}
                >
                  <RefreshCcw />
                  Retry
                </Button>
              </AlertDescription>
            </Alert>
          ) : (
            <div className="flex flex-wrap gap-2">
              {demosQuery.data.demos.map((demo) => (
                <Button
                  key={demo.id}
                  variant="outline"
                  onClick={() => loadDemo(demo)}
                  disabled={renderMutation.isPending}
                >
                  <Wand2 />
                  {demo.name}
                </Button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Conversation</CardTitle>
          <CardDescription>
            Write your own messages and render them
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(onSubmit)}
              className="flex flex-col gap-4"
            >
              <div className="flex flex-col gap-3">
                {fields.map((field, index) => (
                  <div
                    key={field.id}
                    className="flex flex-col gap-2 rounded-lg border p-3 sm:flex-row sm:items-start"
                  >
                    <FormField
                      control={form.control}
                      name={`messages.${index}.speaker_id`}
                      render={({ field: speakerField }) => (
                        <FormItem className="sm:w-32">
                          <FormLabel>Speaker</FormLabel>
                          <Select
                            onValueChange={speakerField.onChange}
                            value={speakerField.value}
                          >
                            <FormControl>
                              <SelectTrigger aria-label="Speaker">
                                <SelectValue placeholder="Speaker" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {SPEAKERS.map((speaker) => (
                                <SelectItem key={speaker} value={speaker}>
                                  {speaker}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name={`messages.${index}.text`}
                      render={({ field: textField }) => (
                        <FormItem className="flex-1">
                          <FormLabel>Message</FormLabel>
                          <FormControl>
                            <Input placeholder="Message" {...textField} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      aria-label="Remove message"
                      className="mt-7"
                      onClick={() => remove(index)}
                      disabled={fields.length <= 1}
                    >
                      <Trash2 />
                    </Button>
                  </div>
                ))}
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => append({ speaker_id: "ada", text: "" })}
                >
                  <Plus />
                  Add message
                </Button>
                <LoadingButton type="submit" loading={renderMutation.isPending}>
                  Render comic
                </LoadingButton>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Preview</CardTitle>
          <CardDescription>Your rendered comic strip</CardDescription>
        </CardHeader>
        <CardContent>
          {renderMutation.isPending ? (
            <div className="flex justify-center py-16">
              <Loader2 className="size-8 animate-spin text-muted-foreground" />
            </div>
          ) : renderMutation.isError ? (
            <Alert variant="destructive">
              <Loader2 />
              <AlertTitle>Render failed</AlertTitle>
              <AlertDescription className="flex flex-col items-start gap-2">
                <span>
                  Something went wrong while rendering the comic. Check your
                  messages and try again.
                </span>
                <Button variant="outline" size="sm" onClick={retry}>
                  <RefreshCcw />
                  Retry
                </Button>
              </AlertDescription>
            </Alert>
          ) : comic ? (
            <ComicStrip comic={comic} />
          ) : (
            <div className="flex flex-col items-center gap-2 py-16 text-center">
              <Wand2 className="size-8 text-muted-foreground" />
              <p className="text-muted-foreground">
                Pick a demo dialogue or write a conversation to see your comic
                here.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Comic
