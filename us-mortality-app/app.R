# DATA608 HW3
# Mael Illien

library(tidyverse)
library(plotly)
library(shiny)

data <- read_csv("https://raw.githubusercontent.com/maelillien/data608/master/module3/data/cleaned-cdc-mortality-1999-2010-2.csv")
data <- data %>% rename(Cause = ICD.Chapter)
data2010 <- data %>% filter(Year==2010)

data_national <- data %>% group_by(Year, Cause) %>% summarize(Avg = round(sum(Deaths)/sum(Population)*100000,1))

# Define UI for application
ui <- fluidPage(
    headerPanel('US Crude Mortality by Cause'),
    fluidRow(
        column(6,plotlyOutput('plot1')),
        column(6,plotlyOutput('plot2'))
    ),
    fluidRow(
        column(3, selectInput('cause', 'Cause', unique(data$Cause), selected='Neoplasms')),
        column(3, selectInput('year', 'Year', unique(data$Year), selected='2010')),
        column(3, selectInput('state', 'State', unique(data$State), selected='NY'))
    )
)

# Define server logic required to draw a bar and line plot
server <- function(input, output, session) {
    output$plot1 <- renderPlotly({
        
        dfSlice <- data %>% filter(Year == input$year & Cause == input$cause)
        # Highlight the selected state
        state_index <- which(dfSlice$State == input$state)
        clist <- rep('#CC1480',length(dfSlice$State))
        clist[state_index] <- '#FF9673'
        # Plot bar sorted bar chart
        plot_ly(dfSlice, x = ~reorder(State, -Crude.Rate), y = ~Crude.Rate, type='bar', marker = list(color=clist)) %>%
            layout(title = "", xaxis = list(title = ""), yaxis = list(title="Crude Rate"))
    })
    
    output$plot2 <- renderPlotly({

        dfSlice <- data %>% filter(State == input$state, Cause == input$cause) %>% inner_join(data_national)
        plot_ly(dfSlice, x = ~Year, y = ~Crude.Rate, name = input$state, type='scatter', mode = 'lines', line = list(color = '#FF9673')) %>%
            add_trace(y = ~Avg, name = 'National Average', line = list(color = '#CC1480')) %>%
                layout(title = "", xaxis = list(title = ""), yaxis = list(title="Crude Rate"))
    })
    
}

# Run the application 
shinyApp(ui = ui, server = server)
