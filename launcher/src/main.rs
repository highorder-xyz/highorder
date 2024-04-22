
use iced::theme;
use iced::widget::{
    button, checkbox, column, container, horizontal_space, image, radio, row, scrollable, slider, text, text_input, toggler, vertical_space
};
use iced::widget::{Button, Column, Container, Slider};
use iced::{window, Alignment, Element, Sandbox, Settings, Color, Font, Length, Pixels};

pub fn main() -> iced::Result {
    let settings: Settings<()> = iced::settings::Settings {
        window: window::Settings {
            size: (480, 320),
            resizable: (true),
            decorations: (true),
            ..Default::default()
        },
        ..Default::default()
    };
    LauncherMain::run(settings)
}

enum PageComponent {
    InstallApp,
    LaunchApp{
        version: String,
        app_folder: String
    },
}

#[derive(Debug, Clone, Copy)]
enum AppMessage {
    LaunchPressed,
    InstallPressed
}

struct LauncherMain {
    page: PageComponent
}

impl Sandbox for LauncherMain {
    type Message = AppMessage;

    fn new() -> Self {
        Self { page: PageComponent::InstallApp{}}
    }

    fn title(&self) -> String {
        return self.page.title()
    }

    fn update(&mut self, message: AppMessage) {
        return self.page.update(message)
    }

    fn view(&self) -> Element<AppMessage> {
        let LauncherMain { page, .. } = self;

        let content: Element<_> = column![
            page.view()
        ]
        .max_width(540)
        .spacing(20)
        .padding(20)
        .into();

        let scrollable = scrollable(
            container(content)
            .width(Length::Fill)
            .center_x(),
        );

        container(scrollable).height(Length::Fill).center_y().into()
    }
}


impl PageComponent {
    fn title(&self) -> String {
        match self{
        PageComponent::InstallApp => { return String::from("Install HighOrder")}
        PageComponent::LaunchApp {..}=>{ return String::from("HighOrder Launcher")}
        }
    }

    fn update(&mut self, message: AppMessage) {
        match message {
            AppMessage::LaunchPressed => {}
            AppMessage::InstallPressed => {},
        }
    }

    fn view(&self) -> Element<AppMessage> {
        match self{
            PageComponent::InstallApp => { return self.view_install()}
            PageComponent::LaunchApp {..}=>{ return self.view_launch()}
        }

    }

    fn view_install(&self) ->Element<AppMessage> {
        column![
            button("install").on_press(AppMessage::InstallPressed)
        ]
        .padding(20)
        .align_items(Alignment::Center)
        .into()
    }

    fn view_launch(&self) ->Element<AppMessage> {
        column![
            button("Launch").on_press(AppMessage::LaunchPressed)
        ]
        .padding(20)
        .align_items(Alignment::Center)
        .into()
    }
}
